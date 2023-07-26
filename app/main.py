from functools import wraps
from urllib.parse import urlparse
from urllib.request import urlopen
from flask import Blueprint, flash, redirect, render_template, request, send_from_directory, url_for
from werkzeug.security import safe_join, generate_password_hash
from flask_login import current_user, login_required, logout_user
from .models import User
from .thumbnails import THUMBNAIL_DIR, gen_thumbnail, get_thumbnail
from .posts import delete_post, get_all_posts, get_post, new_post, Response, update_post
from . import media_manager
from .media_manager import Response as MResponse
from . import DATA_DIR, MEDIA_DIR, TEMP_DIR, db
from .settings import get_setting, set_setting
from datetime import datetime as dt
from ordered_set import OrderedSet
import os
import mimetypes
import shutil
import json

main = Blueprint("main", __name__)

ROWS = 10
COLUMNS = 3

# get random id for uploads
def get_random():
    random = os.urandom(5).hex()
    return random

# stolen from SO
# function to split array into array of arrays of size n
def split_into(n, arr):
    if len(arr) % n:
        yield arr[:len(arr) % n]
    for i in range(len(arr) % n, len(arr), n):
        yield arr[i:i+n]

# previous function but start balanced where beginning will get more items than end
def start_bal_split_into(n, arr):
    for i in range(0, len(arr), n):
        yield arr[i:i+n]

# decorator to limit access to admins
def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.admin:
            return func(*args, **kwargs)
        else:
            flash("You have to be an admin to do that!")
            return redirect(url_for("main.index"))
    return wrapper

# login required only if settings say it is
def login_maybe(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if int(get_setting("login_required", "1")) and not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        else:
            return func(*args, **kwargs)
    return wrapper

def strftime(timestamp):
    return dt.fromtimestamp(timestamp).strftime("%d %b %Y - %H:%M:%S")

# stolen from SO
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def get_all_tags(all_posts):
    tags = set()
    for post in all_posts:
        for tag in post.tags:
            tags.add(tag)
    return tags

# stolen from Python Docs
def get_tree_size(path):
    """Return total size of files in given path and subdirs."""
    total = 0
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            total += get_tree_size(entry.path)
        else:
            total += entry.stat(follow_symlinks=False).st_size
    return total

def get_stats():
    all_posts = get_all_posts()
    posts = len(all_posts)
    tags = len(get_all_tags(all_posts))
    space = sizeof_fmt(get_tree_size(DATA_DIR))
    return {
        "posts": posts,
        "tags": tags,
        "space": space
    }

# main website ui
@main.route("/")
@login_maybe
def index():
    page = int(request.args.get("page") or "1") - 1
    posts = get_all_posts()
    tags = sorted(get_all_tags(posts))

    # filter stuff
    include = json.loads(request.args.get("include") or "[]")
    exclude = json.loads(request.args.get("exclude") or "[]")
    posts = get_all_posts()
    actual_posts = []

    if not include:
        for post in posts:
            actual_posts.append(post)
    for post in posts:
        if all(item in post.tags for item in include):
            actual_posts.append(post)
    for item in exclude:
        for post in actual_posts:
            if item in post.tags:
                actual_posts.remove(post)

    posts = list(OrderedSet(actual_posts))

    # do pagination
    posts = list(split_into(COLUMNS, posts))
    posts = list(start_bal_split_into(ROWS, posts))
    pages = len(posts) or 1

    if page < pages:
        posts = posts[page]
    else:
        posts = []
    return render_template(
        "index.html",
        posts=posts,
        get_thumbnail=get_thumbnail,
        strftime=strftime,
        tags=tags,
        pages=pages,
        page=page,
        include=include,
        exclude=exclude
    )

# post viewing path
@main.route("/post/<post_ts>")
@login_maybe
def post(post_ts):
    if post_ts.isdigit():
        post_ts = int(post_ts)
    post = get_post(post_ts)
    if not post:
        flash("Post not found")
    post_dir = safe_join(MEDIA_DIR, str(post_ts))
    media = []
    if os.path.exists(post_dir):
        files = os.listdir(post_dir)
        files.sort(key=lambda x: int(x.split(".")[0]))
        for file in files:
            media.append({
                "location": f"/media/{post_ts}/{file}",
                "type": mimetypes.guess_type(file)[0].split("/")[0]
            })
    if not media and post:
        flash("Media not found")
    return render_template(
        "post.html",
        post=post,
        media=media,
        strftime=strftime
    )

# post adding paths
@main.route("/add")
@login_required
@admin_only
def add():
    return render_template(
        "add.html",
        session_id=get_random()
    )

@main.route("/add", methods=["POST"])
@login_required
@admin_only
def add_post():
    datetime = request.form.get("datetime")
    source = request.form.get("source") or ""
    tags = request.form.get("tags") or ""
    session_id = request.form.get("session_id") or get_random()

    split_tags = [tag.strip() for tag in tags.split(",")]
    split_tags.sort()
    if len(split_tags) == 1 and split_tags[0] == "":
        split_tags = []

    temp_post_dir = safe_join(TEMP_DIR, session_id)
    temp_post_dir_exists = os.path.exists(temp_post_dir)
    files = []
    if temp_post_dir_exists:
        for file in os.listdir(safe_join(TEMP_DIR, session_id)):
            files.append({
                "location": f"/temp/{session_id}/{file}",
                "type": mimetypes.guess_type(file)[0].split("/")[0],
                "file": file
            })
    files.sort(key=lambda x: int( x["file"].split(".")[0] ))

    if not datetime:
        flash("Date/time can't be empty")
        return render_template(
            "add.html",
            source=source,
            tags=tags,
            session_id=session_id,
            files=files
        )
    datetime = dt.fromisoformat(datetime)
    datetime = round(dt.timestamp(datetime))

    new_post_dir = safe_join(MEDIA_DIR, str(datetime))
    if files:
        if os.path.exists(new_post_dir):
            shutil.rmtree(new_post_dir, ignore_errors=True)
        os.makedirs(new_post_dir, exist_ok=True)
        for index, file in enumerate(files):
            old_file = file["file"]
            old_file_ext = old_file.split(".")[-1]
            new_file = f"{index}.{old_file_ext}"
            old_file_path = safe_join(temp_post_dir, old_file)
            new_file_path = safe_join(new_post_dir, new_file)
            shutil.move(old_file_path, new_file_path)
    if temp_post_dir_exists:
        os.rmdir(temp_post_dir)
    response = new_post(datetime, source=source, tags=split_tags)
    if response["response"] == Response.FAILED:
        flash(response["message"])
        return render_template(
            "add.html",
            datetime=request.form.get("datetime"),
            source=source,
            tags=tags,
            session_id=session_id,
            files=files
        )
    gen_thumbnail(str(datetime))

    return redirect(url_for("main.index"))

# post manipulation paths
@main.route("/post/<post_ts>/delete", methods=["POST"])
@login_required
@admin_only
def delete(post_ts):
    if post_ts.isdigit():
        post_ts = int(post_ts)
    post = get_post(post_ts)
    post = get_post(post_ts)
    if not post:
        flash("Post not found")
        return redirect("main.index")
    if os.path.exists(safe_join(MEDIA_DIR, str(post_ts))):
        shutil.rmtree(safe_join(MEDIA_DIR, str(post_ts)))
    if os.path.exists(safe_join(THUMBNAIL_DIR, f"{post_ts}.webp")):
        os.remove(safe_join(THUMBNAIL_DIR, f"{post_ts}.webp"))
    result = delete_post(post_ts)
    if result["response"] == Response.FAILED:
        flash(result["message"])
    return redirect(url_for("main.index"))

@main.route("/post/<post_ts>/edit")
@login_required
@admin_only
def edit(post_ts):
    session_id = get_random()
    if post_ts.isdigit():
        post_ts = int(post_ts)
    post = get_post(post_ts)
    if not post:
        flash("Post not found")
        return redirect("main.index")
    post_dir = safe_join(MEDIA_DIR, str(post_ts))
    files = []
    if os.path.exists(post_dir):
        for file in os.listdir(post_dir):
            files.append({
                "location": f"/temp/{session_id}/{file}",
                "type": mimetypes.guess_type(file)[0].split("/")[0],
                "file": file
            })
    files.sort(key=lambda x: int( x["file"].split(".")[0] ))

    temp_post_dir = safe_join(TEMP_DIR, session_id)
    if files:
        if os.path.exists(temp_post_dir):
            shutil.rmtree(temp_post_dir, ignore_errors=True)
        os.makedirs(temp_post_dir, exist_ok=True)
        for file in files:
            old_file_path = safe_join(post_dir, file["file"])
            new_file_path = safe_join(temp_post_dir, file["file"])
            shutil.copy(old_file_path, new_file_path)
    datetime = dt.fromtimestamp(post_ts).isoformat()
    return render_template(
        "edit.html",
        datetime=datetime,
        source=post.source,
        tags=", ".join(post.tags),
        session_id=session_id,
        files=files,
        ts=post.timestamp
    )

@main.route("/post/<post_ts>/edit", methods=["POST"])
@login_required
@admin_only
def edit_post(post_ts):
    if post_ts.isdigit():
        post_ts = int(post_ts)
    datetime = request.form.get("datetime")
    source = request.form.get("source") or ""
    tags = request.form.get("tags") or ""
    session_id = request.form.get("session_id") or get_random()

    split_tags = [tag.strip() for tag in tags.split(",")]
    split_tags.sort()
    if len(split_tags) == 1 and split_tags[0] == "":
        split_tags = []

    temp_post_dir = safe_join(TEMP_DIR, session_id)
    temp_post_dir_exists = os.path.exists(temp_post_dir)
    files = []
    if temp_post_dir_exists:
        for file in os.listdir(safe_join(TEMP_DIR, session_id)):
            files.append({
                "location": f"/temp/{session_id}/{file}",
                "type": mimetypes.guess_type(file)[0].split("/")[0],
                "file": file
            })
    files.sort(key=lambda x: int( x["file"].split(".")[0] ))

    if not datetime:
        flash("Date/time can't be empty")
        return render_template(
            "edit.html",
            source=source,
            tags=tags,
            session_id=session_id,
            files=files,
            ts=post_ts
        )
    datetime = dt.fromisoformat(datetime)
    datetime = round(dt.timestamp(datetime))

    response = update_post(post_ts, new_timestamp=datetime, source=source, tags=split_tags)
    if response["response"] == Response.FAILED:
        flash(response["message"])
        return render_template(
            "edit.html",
            datetime=request.form.get("datetime"),
            source=source,
            tags=tags,
            session_id=session_id,
            files=files,
            ts=post_ts
        )

    new_post_dir = safe_join(MEDIA_DIR, str(datetime))
    if files:
        if os.path.exists(new_post_dir):
            shutil.rmtree(new_post_dir, ignore_errors=True)
        os.makedirs(new_post_dir, exist_ok=True)
        for index, file in enumerate(files):
            old_file = file["file"]
            old_file_ext = old_file.split(".")[-1]
            new_file = f"{index}.{old_file_ext}"
            old_file_path = safe_join(temp_post_dir, old_file)
            new_file_path = safe_join(new_post_dir, new_file)
            shutil.move(old_file_path, new_file_path)
    if temp_post_dir_exists:
        os.rmdir(temp_post_dir)
    gen_thumbnail(str(datetime))

    return redirect(url_for("main.index"))

# media upload/generation paths
@main.route("/upload", methods=["POST"])
@login_required
@admin_only
def upload():
    session_id = request.args.get("id")
    files = list(request.files.values())
    if not session_id:
        return "No session id provided", 400
    if not files:
        return {"files": []}, 400
    upload_path = safe_join(TEMP_DIR, session_id)
    os.makedirs(upload_path, exist_ok=True)
    start_index = 0
    existing_files = os.listdir(upload_path)
    if existing_files:
        existing_files.sort(key=lambda x: int( x.split(".")[0] ))
        start_index = int( existing_files[-1].split(".")[0] ) + 1
    uploaded_files = []
    for index, file in enumerate(files):
        index += start_index
        name = file.filename or "0.png"
        ext = name.split(".")[-1]
        new_filename = f"{index}.{ext}"
        uploaded_files.append({
            "location": f"/temp/{session_id}/{new_filename}",
            "type": mimetypes.guess_type(new_filename)[0].split("/")[0],
            "file": new_filename
        })
        new_path = safe_join(upload_path, new_filename)
        file.save(new_path)
    uploaded_files.sort(key=lambda x: int( x["file"].split(".")[0] ))
    return {
        "files": uploaded_files
    }

@main.route("/upload_social", methods=["POST"])
@login_required
@admin_only
def upload_social():
    session_id = request.args.get("id")
    media_url = request.get_data().decode("UTF-8")
    if not session_id:
        return "No session id provided", 400
    twitter_cookie = get_setting("twitter_cookie", "")
    media_manager.twitter_manager.set_cookie(twitter_cookie)
    response = media_manager.get_image_links(media_url)
    if response["response"] != MResponse.SUCCESS:
        return response
    links = response["links"]
    upload_path = safe_join(TEMP_DIR, session_id)
    os.makedirs(upload_path, exist_ok=True)
    start_index = 0
    existing_files = os.listdir(upload_path)
    if existing_files:
        existing_files.sort(key=lambda x: int( x.split(".")[0] ))
        start_index = int( existing_files[-1].split(".")[0] ) + 1
    uploaded_files = []
    for index, link in enumerate(links):
        index += start_index
        parsed_link = urlparse(link)
        name = parsed_link.path
        ext = name.split(".")[-1]
        new_filename = f"{index}.{ext}"
        uploaded_files.append({
            "location": f"/temp/{session_id}/{new_filename}",
            "type": mimetypes.guess_type(new_filename)[0].split("/")[0],
            "file": new_filename
        })
        new_path = safe_join(upload_path, new_filename)
        dl_req = urlopen(link)
        data = dl_req.read()
        with open(new_path, "wb") as output:
            output.write(data)
    uploaded_files.sort(key=lambda x: int( x["file"].split(".")[0] ))
    return {
        "response": "success",
        "files": uploaded_files
    }

# media manipulation methods
@main.route("/media_up", methods=["POST"])
@login_required
@admin_only
def media_up():
    session_id = request.args.get("id")
    if not session_id:
        return "No session id provided", 400
    move_file = request.get_data().decode("UTF-8")
    temp_post_dir = safe_join(TEMP_DIR, session_id)
    files = []
    if os.path.exists(temp_post_dir):
        files = os.listdir(safe_join(TEMP_DIR, session_id))
    files.sort(key=lambda x: int( x.split(".")[0] ))
    if move_file in files:
        new_index = files.index(move_file) - 1
        random = get_random()
        if new_index >= 0:
            # file 1 is the requested file
            # file 2 is the other file already in place
            f1_num = move_file.split(".")[0]
            f2_num = files[new_index].split(".")[0]
            f1_ext = move_file.split(".")[1]
            f2_ext = files[new_index].split(".")[1]

            os.rename(safe_join(temp_post_dir, move_file), safe_join(temp_post_dir, f"{random}.{f1_ext}"))
            os.rename(safe_join(temp_post_dir, files[new_index]), safe_join(temp_post_dir, f"{f1_num}.{f2_ext}"))
            os.rename(safe_join(temp_post_dir, f"{random}.{f1_ext}"), safe_join(temp_post_dir, f"{f2_num}.{f1_ext}"))
    return "OK"

@main.route("/media_down", methods=["POST"])
@login_required
@admin_only
def media_down():
    session_id = request.args.get("id")
    if not session_id:
        return "No session id provided", 400
    move_file = request.get_data().decode("UTF-8")
    temp_post_dir = safe_join(TEMP_DIR, session_id)
    files = []
    if os.path.exists(temp_post_dir):
        files = os.listdir(safe_join(TEMP_DIR, session_id))
    files.sort(key=lambda x: int( x.split(".")[0] ))
    if move_file in files:
        new_index = files.index(move_file) + 1
        random = get_random()
        if new_index < len(files):
            # file 1 is the requested file
            # file 2 is the other file already in place
            f1_num = move_file.split(".")[0]
            f2_num = files[new_index].split(".")[0]
            f1_ext = move_file.split(".")[1]
            f2_ext = files[new_index].split(".")[1]

            os.rename(safe_join(temp_post_dir, move_file), safe_join(temp_post_dir, f"{random}.{f1_ext}"))
            os.rename(safe_join(temp_post_dir, files[new_index]), safe_join(temp_post_dir, f"{f1_num}.{f2_ext}"))
            os.rename(safe_join(temp_post_dir, f"{random}.{f1_ext}"), safe_join(temp_post_dir, f"{f2_num}.{f1_ext}"))
    return "OK"

@main.route("/media_delete", methods=["POST"])
@login_required
@admin_only
def media_delete():
    session_id = request.args.get("id")
    if not session_id:
        return "No session id provided", 400
    delete_file = request.get_data().decode("UTF-8")
    temp_post_dir = safe_join(TEMP_DIR, session_id)
    file_path = safe_join(temp_post_dir, delete_file)

    os.remove(file_path)

    return delete_file

# website setting paths
@main.route("/settings")
@login_required
def settings():
    allow_signups = int(get_setting("allow_signups", "1"))
    login_required = int(get_setting("login_required", "1"))
    twitter_cookie = get_setting("twitter_cookie", "")
    users = [user.username for user in User.query.all()]
    users.remove(current_user.username)
    return render_template(
        "settings.html",
        allow_signups=allow_signups,
        login_required=login_required,
        twitter_cookie=twitter_cookie,
        users=users,
        stats=get_stats()
    )

@main.route("/settings", methods=["POST"])
@login_required
@admin_only
def settings_post():
    allow_signups = request.form.get("allow_signups")
    allow_signups = "1" if allow_signups == "on" else "0"
    login_required = request.form.get("login_required")
    login_required = "1" if login_required == "on" else "0"
    app_name = request.form.get("app_name") 
    app_name = app_name or get_setting("app_name", "Art Downloader")
    twitter_cookie = request.form.get("twitter_cookie") 
    twitter_cookie = twitter_cookie or get_setting("twitter_cookie", "")

    set_setting("allow_signups", allow_signups)
    set_setting("login_required", login_required)
    set_setting("app_name", app_name)
    set_setting("twitter_cookie", twitter_cookie)
    media_manager.twitter_manager.set_cookie(twitter_cookie)
    return redirect(url_for("main.settings"))

# user setting paths
@main.route("/user_settings", methods=["POST"])
@login_required
def user_settings_post():
    username = request.form.get("username")
    password = request.form.get("password")

    old_username = current_user.username
    user = User.query.filter_by(username=old_username).first()
    new_user = User.query.filter_by(username=username).first()

    if new_user and username == current_user.username:
        flash("Username taken!")
        return redirect(url_for("main.settings"))

    if username:
        user.username = username

    if password:
        user.password = generate_password_hash(password)

    db.session.commit()
    return redirect(url_for("main.settings"))

@main.route("/delete_own_account", methods=["POST"])
@login_required
def delete_own_account():
    if current_user.admin:
        flash("As an admin, you can't delete your own account. You can however delete other admin accounts.")
        return redirect(url_for("main.settings"))
    user = User.query.filter_by(username=current_user.username).first()

    db.session.delete(user)
    db.session.commit()

    logout_user()
    return redirect(url_for("auth.login"))

@main.route("/user/<username>")
@login_required
@admin_only
def user(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("User doesn't exist!")
        return redirect(url_for("main.settings"))

    if current_user.username == username:
        flash("Can't open that page on yourself!")
        return redirect(url_for("main.settings"))

    return render_template(
        "user.html",
        username=username,
        admin=user.admin
    )

@main.route("/user/<username>/delete_account", methods=["POST"])
@login_required
@admin_only
def delete_account(username):
    if current_user.username == username:
        flash("As an admin, you can't delete your own account. You can however delete other admin accounts.")
        return redirect(url_for("main.settings"))
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("User doesn't exist!")
        return redirect(url_for("main.settings"))

    db.session.delete(user)
    db.session.commit()

    flash(f"Successfully deleted {username}'s account!")
    return redirect(url_for("main.settings"))

# user setting paths
@main.route("/user/<username>/user_settings", methods=["POST"])
@login_required
@admin_only
def indiv_user_settings_post(username):
    new_username = request.form.get("username")
    password = request.form.get("password")
    admin = request.form.get("admin") == "on"

    user = User.query.filter_by(username=username).first()
    new_user = User.query.filter_by(username=new_username).first()

    if not user:
        flash("User doesn't exist!")
        return redirect(url_for("main.settings"))

    if new_user and new_username != username:
        flash("Username taken!")
        return redirect(url_for("main.user", username=username))

    if new_username:
        user.username = new_username

    if password:
        user.password = generate_password_hash(password)

    user.admin = admin

    db.session.commit()
    return redirect(url_for("main.user", username=new_username or username))

# preview paths
@main.route("/media/<path:path>")
@login_maybe
def serve_media(path):
    return send_from_directory(MEDIA_DIR, path)

@main.route("/thumb/<path>")
@login_maybe
def serve_thumbnail(path):
    thumb_dir = os.path.join(DATA_DIR, "thumbnails")
    return send_from_directory(thumb_dir, path)

@main.route("/temp/<path:path>")
@login_required
@admin_only
def serve_temp(path):
    return send_from_directory(TEMP_DIR, path)
