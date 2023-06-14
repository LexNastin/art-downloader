from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
# from . import media_manager
from .settings import get_setting, set_setting

main = Blueprint("main", __name__)

@main.route("/")
@login_required
def index():
    return render_template("index.html")

@main.route("/add")
@login_required
def add():
    return render_template("add.html")

@main.route("/settings")
@login_required
def settings():
    allow_signups = int(get_setting("allow_signups", "1"))
    return render_template("settings.html", allow_signups=allow_signups)

@main.route("/settings", methods=["POST"])
@login_required
def settings_post():
    allow_signups = ("1" if request.form.get("allow_signups") == "on" else "0") or "1"
    print(allow_signups)

    set_setting("allow_signups", allow_signups)
    return redirect(url_for("main.settings"))
