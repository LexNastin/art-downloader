from flask import Blueprint, render_template
from flask_login import login_required
# from . import media_manager

main = Blueprint("main", __name__)

@main.route("/")
@login_required
def index():
    return render_template("index.html")

@main.route("/add")
@login_required
def add():
    return render_template("add.html")
