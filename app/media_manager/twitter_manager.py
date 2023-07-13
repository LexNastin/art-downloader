import requests
from http.cookies import SimpleCookie
import json
import re
from .response import Response

ROOT_URL = "https://twitter.com"
AUTHORIZATION = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

class Twitter:
    def __init__(self, log_level=1):
        self.log_level = log_level
        self._log("Loading guest cookie...")
        try:
            self.guest_token = self._get_guest_token()
        except:
            self._log("Failed to load guest cookie")
        self._log("Guest cookie loaded")

    def _log(self, text):
        if self.log_level >= 1:
            print(f"TwitterMan: {text}")

    def _debug(self, text):
        if self.log_level >= 2:
            print(f"TwitterMan: {text}")

    def _get_guest_token(self):
        # now = str(round(datetime.now().timestamp() * 1000))
        # guest_token_request = requests.get(f"{ROOT_URL}/?logout={now}", allow_redirects=False)
        # guest_token_cookie_text = guest_token_request.headers["set-cookie"]
        # guest_token_cookie = SimpleCookie()
        # guest_token_cookie.load(guest_token_cookie_text)
        # cookie_loaded = True
        # try:
        #     guest_token = guest_token_cookie["guest_id"].value.split("%3A")[-1]
        # except KeyError:
        #     cookie_loaded = False
        # if not cookie_loaded:
        #     raise Exception("Error in guest token retrieval")
        twitter_html = requests.get(ROOT_URL).text
        twitter_cookies = re.findall(r'document.cookie="(.*?)"', twitter_html)
        if len(twitter_cookies) == 0:
            raise Exception("Error in guest token retrieval")
        guest_token_cookie = SimpleCookie()
        guest_token_cookie.load(twitter_cookies[0])
        cookie_loaded = True
        try:
            guest_token = guest_token_cookie["gt"].value
        except KeyError:
            cookie_loaded = False
        if not cookie_loaded:
            raise Exception("Error in guest token retrieval")
        self._debug(f"Get cookie is {guest_token}")
        return guest_token

    def _try_get_tweet_details(self, tweet_id):
        self._debug(f"Getting TweetDetail for {tweet_id}...")
        request_headers = {
            "authorization": AUTHORIZATION,
            "x-guest-token": self.guest_token
        }
        request_body = {
            "focalTweetId": str(tweet_id),
            "with_rux_injections": True,
            "includePromotedContent": True,
            "withCommunity": True,
            "withTweetQuoteCount": True,
            "withBirdwatchNotes": True,
            "withSuperFollowsUserFields": True,
            "withUserResults": True,
            "withBirdwatchPivots": True,
            "withReactionsMetadata": True,
            "withReactionsPerspective": True,
            "withSuperFollowsTweetFields": True,
            "withVoice": True
        }
        request_url = f"{ROOT_URL}/i/api/graphql/kUnCMgMYZCR8GyRZz76IQg/TweetDetail"

        request_body = {
            "variables": json.dumps(request_body)
        }
        request = requests.get(request_url, params=request_body, headers=request_headers)
        self._debug(f"Request responded with code {request.status_code}")
        return request

    def get_tweet_details(self, tweet_id):
        tweet_details = self._try_get_tweet_details(tweet_id)
        if tweet_details.status_code == 403:
            self._debug("Authorization required, trying to get new guest token...")
            self._get_guest_token()
        if tweet_details.status_code != 200:
            self._debug("Trying to get tweet again...")
        if tweet_details.status_code != 200:
            raise Exception(f"Something went wrong trying to get tweet {tweet_id}")
        found = "errors" not in tweet_details.json()
        if not found:
            self._debug(f"Couldn't find tweet {tweet_id}")
            return None
        self._debug(f"Successfully got TweetDetail for {tweet_id}")
        return tweet_details.json()

class TwitterManager:
    def __init__(self):
        self.tm = Twitter(log_level=0)

    def get_image_links(self, url):
        try:
            tweet_id = re.findall(r"/status/(\d+)", url)[0]
            tweeter = re.findall(r"twitter.com/(.*?)/status/\d+", url)[0]
            tweet_details = self.tm.get_tweet_details(tweet_id)
            links = []
            # [[(item["media_url_https"], item["type"]) for item in entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"]] for entry in tweet_details["data"]["threaded_conversation_with_injections_v2"]["instructions"][0]["entries"] if "1623577224346497025" in entry["entryId"]]
            if not tweet_details:
                return {
                    "response": Response.REMOVED
                }

            # parse root tweet
            tweet_entities = tweet_details["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"]
            if tweet_entities[0]["content"]["itemContent"]["itemType"] == "TimelineTombstone":
                return {
                    "response": Response.REMOVED
                }
            if "quoted_status_permalink" in tweet_entities[0]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]:
                if "extended_entities" not in tweet_entities[0]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]:
                    new_url = tweet_entities[0]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["quoted_status_permalink"]["expanded"]
                    tweet_id = re.findall(r"/status/(\d+)", new_url)[0]
                    tweeter = re.findall(r"twitter.com/(.*?)/status/\d+", new_url)[0]
                    tweet_details = self.tm.get_tweet_details(tweet_id)
                    tweet_entities = tweet_details["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"]
            media_entities = []
            for entry in tweet_entities:
                if tweet_id in entry["entryId"]:
                    if "tweet" in entry["content"]["itemContent"]["tweet_results"]["result"]:
                        entry["content"]["itemContent"]["tweet_results"]["result"] = entry["content"]["itemContent"]["tweet_results"]["result"]["tweet"]
                    if "extended_entities" in entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"]:
                        media_entities = entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"]
                        break
            # tweet_entities = [entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"] for entry in tweet_details["data"]["threaded_conversation_with_injections_v2"]["instructions"][0]["entries"] if tweet_id in entry["entryId"] and "extended_entities" in entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"]][0]
            if not media_entities:
                return {
                    "response": Response.FAILED,
                    "message": "Not a media post!"
                }
            for entry in media_entities:
                if entry["type"] == "photo":
                    links.append(entry["media_url_https"])
                elif entry["type"] == "video":
                    videos = entry["video_info"]["variants"]
                    videos.sort(key=lambda x: x["bitrate"] if "bitrate" in x else 0)
                    video_url = videos[-1]["url"]
                    links.append(video_url)

            # parse continued tweets
            reply_entities = tweet_details["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"]
            reply_thread = []
            for entry in reply_entities:
                if "conversationthread" in entry["entryId"]:
                    if entry["content"]["items"][0]["item"]["itemContent"]["itemType"] != "TimelineTombstone":
                        if "legacy" not in entry["content"]["items"][0]["item"]["itemContent"]["tweet_results"]["result"]:
                            entry["content"]["items"][0]["item"]["itemContent"]["tweet_results"]["result"] = entry["content"]["items"][0]["item"]["itemContent"]["tweet_results"]["result"]["tweet"]
                        if entry["content"]["items"][0]["item"]["itemContent"]["tweet_results"]["result"]["core"]["user_results"]["result"]["legacy"]["screen_name"].lower() == tweeter.lower():
                            if entry["content"]["items"][0]["item"]["itemContent"]["tweet_results"]["result"]["legacy"]["in_reply_to_status_id_str"] == tweet_id:
                                reply_thread = entry
                                break
            if reply_thread:
                reply_thread = [tweet["item"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"] for tweet in reply_thread["content"]["items"] if tweet["item"]["itemContent"]["itemType"] == "TimelineTweet" and "extended_entities" in tweet["item"]["itemContent"]["tweet_results"]["result"]["legacy"]]
            # reply_entities = [
            #         [
            #             tweet["item"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"] for tweet in entry["content"]["items"]
            #             if tweet["item"]["itemContent"]["itemType"] == "TimelineTweet" and "extended_entities" in tweet["item"]["itemContent"]["tweet_results"]["result"]["legacy"]]
            #
            #         for entry in tweet_details["data"]["threaded_conversation_with_injections_v2"]["instructions"][0]["entries"] if "conversationthread" in entry["entryId"]
            #         and "tombstone" not in entry["content"]["items"][0]["item"]["itemContent"]["tweet_results"]["result"]
            #         and entry["content"]["items"][0]["item"]["itemContent"]["tweet_results"]["result"]["legacy"]["in_reply_to_status_id_str"] == tweet_id
            #     ][0]
            response_type = Response.SUCCESS
            for tweet in reply_thread:
                for entry in tweet:
                    if entry["type"] == "photo":
                        links.append(entry["media_url_https"])
                    elif entry["type"] == "video":
                        videos = entry["video_info"]["variants"]
                        videos.sort(key=lambda x: x["bitrate"] if "bitrate" in x else 0)
                        video_url = videos[-1]["url"]
                        links.append(video_url)
                    else:
                        response_type = Response.INCOMPLETE
                        continue
            return {
                "response": response_type,
                "links": links
            }
        except Exception as e:
            return {
                "response": Response.FAILED,
                "message": repr(e)
            }
