from .models import Post
from . import db
import json
from enum import Enum

class Response(Enum):
    SUCCESS = 1
    FAILED = 2

def get_post(timestamp):
    post = Post.query.filter_by(timestamp=timestamp).first()
    if not post:
        return None
    new_post = Post(timestamp=post.timestamp, source=post.source, tags=json.loads(post.tags))

    return new_post

def get_all_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()

    new_posts = []
    for post in posts:
        new_post = Post(timestamp=post.timestamp, source=post.source, tags=json.loads(post.tags))
        new_posts.append(new_post)

    return new_posts

def new_post(timestamp, source="", tags=[]):
    post = Post.query.filter_by(timestamp=timestamp).first()

    if not post:
        new_setting = Post(timestamp=timestamp, source=source, tags=json.dumps(tags))

        db.session.add(new_setting)
        db.session.commit()
        return {
            "response": Response.SUCCESS
        }
    else:
        return {
            "response": Response.FAILED,
            "message": "A post already exists at that time"
        }

def delete_post(timestamp):
    post = Post.query.filter_by(timestamp=timestamp).first()
    if not post:
        return {
            "response": Response.FAILED,
            "message": "Couldn't delete post. It didn't exist"
        }
    db.session.delete(post)
    db.session.commit()
    return {
        "response": Response.SUCCESS
    }

def update_post(timestamp, new_timestamp=None,source=None, tags=None):
    post = Post.query.filter_by(timestamp=timestamp).first()

    if new_timestamp and timestamp != new_timestamp:
        existing_post = Post.query.filter_by(new_timestamp)

        if existing_post:
            return {
                "response": Response.FAILED,
                "message": "A post already exists at that time"
            }

    if post:
        post.timestamp = new_timestamp or post.timestamp
        post.source = source or post.source
        post.tags = json.dumps(tags) if tags != None else post.tags
        db.session.commit()
        return {
            "response": Response.SUCCESS
        }
    else:
        return {
            "response": Response.FAILED,
            "message": "This post doesn't exist"
        }
