import requests
import html
import json
from .response import Response

class RedditManager:
    def get_image_links(self, url):
        try:
            data_url = url.split("?")[0] + ".json"
            post_data_text = requests.get(data_url, headers={
                "User-Agent": "linux:favourite_art_scraper:v0.1 (by: /u/archgryphon9362)"
            })
            remaining = int(post_data_text.headers["X-Ratelimit-Remaining"])
            reset = int(post_data_text.headers["X-Ratelimit-Reset"])
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
            elif "media_metadata" in valuable:
                media = [item["s"] for item in valuable["media_metadata"].values()]
                new_media = []
                for value in media:
                    link = [link for link in value.values() if "http" in str(link)]
                    if len(link) > 0:
                        new_media.append(html.unescape(link[0]))
                media = new_media
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
                "links": media
            }
        except Exception as e:
            return {
                "response": Response.FAILED,
                "message": repr(e)
            }
