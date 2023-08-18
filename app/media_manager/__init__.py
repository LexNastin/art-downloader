import os
from .insta_manager import InstaManager
from .reddit_manager import RedditManager
from .tumblr_manager import TumblrManager
from .twitter_manager import TwitterManager
import requests
import re
from .response import Response
from urllib.parse import urlparse

class MediaManager:
    def __init__(self):
        self.insta_manager = InstaManager()
        self.reddit_manager = RedditManager()
        self.tumblr_manager = TumblrManager()
        self.twitter_manager = TwitterManager()

    def get_image_links(self, link):
        try:
            parsed = urlparse(link)
            supported = ["png", "jpg", "jpeg", "mp4", "avif", "heic", "heif", "webm", "webp"]
            extension = parsed.path.split(".")[-1].lower()
        except Exception as e:
            return {
                "response": Response.FAILED,
                "message": repr(e)
            }

        if any(extension == current_ext for current_ext in supported):
            return {
                "response": Response.SUCCESS,
                "links": [link]
            }
        elif "instagram.com" in link:
            return self.insta_manager.get_image_links(link)
        elif "reddit.com" in link:
            return self.reddit_manager.get_image_links(link)
        elif "tumblr.com" in link:
            # fix all "at.tumblr.com" redirects to go where they need to removing streams and unknowns and users
            if "at.tumblr" in link:
                try:
                    actual = requests.get(link, allow_redirects=False).headers["Location"]
                except:
                    return {
                        "response": Response.FAILED,
                        "message": "Failed to convert Tumblr short link"
                    }
                if "key_live" in link or "/search/" in actual:
                    return {
                        "response": Response.FAILED,
                        "message": "Live Tumblr links not supported"
                    }
                link = actual
            # fixing links that are on custom pages to be on general tumblr
            if ".tumblr.com" in link and "www.tumblr" not in link:
                poster = re.findall(r"//(.*)\.tumblr.com/post", link)[0]
                link = link.replace(poster, "www")
                link = link.replace("/post/", f"/{poster}/")
            return self.tumblr_manager.get_image_links(link)
        elif "twitter.com" in link or "x.com" in link:
            return self.twitter_manager.get_image_links(link)
        else:
            return {
                "response": Response.UNSUPPORTED
            }
