from functools import wraps
from flask import Blueprint, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from .thumbnails import get_thumbnail
from .models import Post
from .posts import get_all_posts, get_post, new_post, Response
# from . import media_manager
from . import DATA_DIR, MEDIA_DIR
from .settings import get_setting, set_setting
from datetime import datetime as dt
import os
import mimetypes

main = Blueprint("main", __name__)

def split_into(n, arr):
    for i in range(0, len(arr), n):
        yield arr[i:i+n]

def admin_only(func):
    @wraps(func)
    def wrapper():
        if current_user.is_authenticated and current_user.admin:
            return func()
        else:
            flash("You have to be an admin to do that!")
            return redirect(url_for("main.index"))
    return wrapper

@main.route("/")
@login_required
def index():
    posts = get_all_posts()
    return render_template("index.html", posts=list(split_into(3, posts)), get_thumbnail=get_thumbnail)

@main.route("/post")
@login_required
def post():
    post_ts = request.args.get("ts")
    if post_ts.isdigit():
        post_ts = int(post_ts)
    post = get_post(post_ts)
    if not post:
        flash("Post not found")
    post_dir = os.path.join(MEDIA_DIR, str(post_ts))
    media = []
    if os.path.exists(post_dir):
        for file in os.listdir(post_dir):
            media.append({
                "location": f"/media/{post_ts}/{file}",
                "type": mimetypes.guess_type(file)[0].split("/")[0]
            })
    if not media and post:
        flash("Media not found")
    return render_template("post.html", post=post, media=media)

@main.route("/add")
@login_required
@admin_only
def add():
    return render_template("add.html")

@main.route("/add", methods=["POST"])
@login_required
@admin_only
def add_post():
    datetime = request.form.get("datetime")
    source = request.form.get("source") or ""
    tags = request.form.get("tags") or ""
    split_tags = [tag.strip() for tag in tags.split(",")]

    if not datetime:
        flash("Date/time can't be empty")
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
@admin_only
def settings_post():
    allow_signups = request.form.get("allow_signups")
    allow_signups = "1" if allow_signups == "on" else "0"
    app_name = request.form.get("app_name") 
    app_name = app_name or get_setting("app_name", "Art Downloader")

    set_setting("allow_signups", allow_signups)
    set_setting("app_name", app_name)
    return redirect(url_for("main.settings"))

@main.route("/media/<path:path>")
@login_required
def serve_media(path):
    return send_from_directory(MEDIA_DIR, path)

@main.route("/thumb/<path:path>")
@login_required
def serve_thumbnail(path):
    thumb_dir = os.path.join(DATA_DIR, "thumbnails")
    return send_from_directory(thumb_dir, path)
