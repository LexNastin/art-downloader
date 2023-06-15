from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from .models import Post
from .posts import get_all_posts, new_post, Response
# from . import media_manager
from .settings import get_setting, set_setting
from datetime import datetime as dt

main = Blueprint("main", __name__)

@main.route("/")
@login_required
def index():
    posts = get_all_posts()
    return render_template("index.html", posts=posts)

@main.route("/add")
@login_required
def add():
    return render_template("add.html")

@main.route("/add", methods=["POST"])
@login_required
def add_post():
    datetime = request.form.get("datetime")
    source = request.form.get("source") or ""
    tags = request.form.get("tags") or ""
    split_tags = [tag.strip() for tag in tags.split(",")]

    if not datetime:
        flash("Date/Time can't be empty")
        return render_template("add.html", source=source, tags=tags)
    datetime = dt.fromisoformat(datetime)
    datetime = round(dt.timestamp(datetime))

    split_tags = [tag.strip() for tag in tags.split(",")]
    response = new_post(datetime, source=source, tags=split_tags)
    if response["response"] == Response.FAILED:
        flash(response["message"])
        return render_template("add.html", datetime=datetime, source=source, tags=tags)

    return redirect(url_for("main.index"))

@main.route("/settings")
@login_required
def settings():
    allow_signups = int(get_setting("allow_signups", "1"))
    return render_template("settings.html", allow_signups=allow_signups)

@main.route("/settings", methods=["POST"])
@login_required
def settings_post():
    allow_signups = request.form.get("allow_signups")
    allow_signups = "1" if allow_signups == "on" else "0"
    app_name = request.form.get("app_name") 
    app_name = app_name or get_setting("app_name", "Art Downloader")

    set_setting("allow_signups", allow_signups)
    set_setting("app_name", app_name)
    return redirect(url_for("main.settings"))
