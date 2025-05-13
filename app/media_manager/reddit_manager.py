import requests
import html
import json
from .response import Response
from urllib.parse import urljoin, urlparse

class RedditManager:
    def get_image_links(self, url):
        try:
            redirect = requests.head(url).headers["location"]
            if redirect:
                url = urljoin(url, redirect)

            data_url = url.split("?")[0] + ".json"
            post_data_text = requests.get(data_url, headers={
                "User-Agent": "linux:favourite_art_scraper:v0.1 (by: /u/archgryphon9362)"
            })
            remaining = float(post_data_text.headers["X-Ratelimit-Remaining"])
            reset = float(post_data_text.headers["X-Ratelimit-Reset"])
            post_data_text = post_data_text.text
            post_data = json.loads(post_data_text)
            response_type = Response.SUCCESS
            if "error" in post_data and post_data["error"] == 404:
                return {
                    "response": Response.REMOVED
                }
            elif "error" in post_data:
                return {
                    "response": Response.FAILED,
                    "message": "Failed for unknown reason"
                }
            valuable = post_data[0]["data"]["children"][0]["data"]
            if valuable["removed_by_category"] != None:
                return {
                    "response": Response.REMOVED
                }
            if valuable["media"] and valuable["media"]["reddit_video"]:
                media = [html.unescape(valuable["media"]["reddit_video"]["hls_url"])]
                return {
                    "response": Response.FAILED,
                    "message": "Reddit videos are currently unsupported"
                }
            elif "preview" in valuable:
                media = valuable["preview"]["images"]
                if len(media) > 1 or "media_metadata" in valuable:
                    response_type = Response.INCOMPLETE
                media = media[0]
                if media["variants"] != {} and "obfuscated" not in media["variants"]:
                    media = [html.unescape(list(media["variants"].values())[0]["source"]["url"])]
                else:
                    media = [html.unescape(media["source"]["url"])]
            elif "media_metadata" in valuable and "gallery_data" in valuable:
                ids = [item["media_id"] for item in valuable["gallery_data"]["items"]]
                media = []
                for id in ids:
                    src = valuable["media_metadata"][id]["s"]
                    media.append(src)
                new_media = []
                for value in media:
                    link = [link for link in value.values() if "http" in str(link)]
                    if len(link) > 0:
                        new_media.append(html.unescape(link[0]))
                media = new_media
            elif "url" in valuable:
                media = []
                supported_exts = ["png", "jpg", "jpeg", "mp4", "avif", "heic", "heif", "webm", "webp"]
                extension = urlparse(valuable["url"]).path.split(".")[-1].lower()
                if any(extension.startswith(current_ext) for current_ext in supported_exts):
                    media.append(valuable["url"])
            else:
                return {
                    "response": Response.FAILED,
                    "message": "Couldn't find anything in the post"
                }
            if remaining < 2:
                return {
                    "response": Response.RATE_LIMITED,
                    "time": {reset}
                }
            return {
                "response": response_type,
                "links": media,
                "url": url
            }
        except Exception as e:
            return {
                "response": Response.FAILED,
                "message": repr(e)
            }
