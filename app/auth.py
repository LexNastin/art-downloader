from flask import Blueprint, redirect, render_template, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import current_user, login_required, login_user, logout_user
from .settings import get_setting

auth = Blueprint("auth", __name__)

@auth.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if not User.query.all():
        return redirect(url_for("auth.signup"))
    return render_template("login.html")

@auth.route("/login", methods=["POST"])
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        flash("Wrong username or password")
        return redirect(url_for("auth.login"))

    login_user(user, remember=True)
    next = request.args.get("next")
    if next:
        return redirect(next)
    return redirect(url_for("main.index"))

@auth.route("/signup")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    allow_signups = int(get_setting("allow_signups", "1"))
    if not allow_signups:
        return render_template("signup_disabled.html")
    return render_template("signup.html")

@auth.route("/signup", methods=["POST"])
def signup_post():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    allow_signups = int(get_setting("allow_signups", "1"))
    if not allow_signups:
        return redirect(url_for("auth.signup"))
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()

    if user:
        flash("Username taken!")
        return redirect(url_for("auth.signup"))

    admin = False if User.query.filter_by(admin=True).first() else True

    hash = generate_password_hash(password)
    new_user = User(username=username, password=hash, admin=admin)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
