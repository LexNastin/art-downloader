import json
import re
import requests
from .response import Response

class InstaManager:
    def _get_img(_, media, candidates):
        w = media["original_width"]
        h = media["original_height"]
        for candidate in candidates:
            if candidate["width"] == w and candidate["height"] == h:
                return candidate["url"]
        return candidates[0]["url"]

    def get_image_links(self, link):
        try:
            id = re.findall(r"instagram.com/(?:(?:p)|(?:reel))/([a-zA-Z\-0-9_]+)/?", link)[0]
            variables = {
                "shortcode": id
            }
            request_data = {
                "variables": json.dumps(variables),
                "doc_id": "6122460227882894"
            }
            result = requests.post("https://www.instagram.com/api/graphql", request_data, headers={"user-agent": "my fan art downloader"})
            code = result.status_code
            result = result.json()
            links = []
            if code != 200:
                return {
                    "response": Response.FAILED,
                    "message": f"HTTP response code was {code}"
                }
            if result["data"] == None:
                return {
                    "response": Response.REMOVED
                }
            data = result["data"]["xdt_api__v1__media__shortcode__web_info"]["items"][0]
            if data["carousel_media"] != None:
                for item in data["carousel_media"]:
                    if item["video_versions"] != None:
                        candidates = item["video_versions"]
                    else:
                        candidates = item["image_versions2"]["candidates"]
                    url = self._get_img(item, candidates)
                    links.append(url)
            else:
                if data["video_versions"] != None:
                    candidates = data["video_versions"]
                else:
                    candidates = data["image_versions2"]["candidates"]
                url = self._get_img(candidates)
                links.append(url)
            if not links:
                return {
                    "response": Response.FAILED,
                    "message": "Couldn't find anything in the post"
                }
            return {
                "response": Response.SUCCESS,
                "links": links
            }
        except Exception as e:
            return {
                "response": Response.FAILED,
                "message": repr(e)
            }
