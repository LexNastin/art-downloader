from flask import Blueprint, render_template
# from . import media_manager

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/add")
def add():
    return render_template("add.html")
