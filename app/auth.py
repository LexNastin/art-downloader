from flask import Blueprint, redirect, render_template, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

auth = Blueprint("auth", __name__)

@auth.route("/login")
def login():
    return render_template("login.html")

@auth.route("/login", methods=["POST"])
def login_post():
    return redirect(url_for("main.index"))

@auth.route("/signup")
def signup():
    return render_template("signup.html")

@auth.route("/signup", methods=["POST"])
def signup_post():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()

    if user:
        flash("Username taken!")
        return redirect(url_for("auth.signup"))

    hash = generate_password_hash(password)
    new_user = User(username=username, password=hash)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))

@auth.route("/logout")
def logout():
    return redirect(url_for("auth.login"))
