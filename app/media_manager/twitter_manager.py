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
        self.cookie = ""

    def _log(self, text):
        if self.log_level >= 1:
            print(f"TwitterMan: {text}")

    def _debug(self, text):
        if self.log_level >= 2:
            print(f"TwitterMan: {text}")

    def _try_get_tweet_details(self, tweet_id):
        self._debug(f"Getting TweetDetail for {tweet_id}...")
        cookie_parser = SimpleCookie()
        cookie_parser.load(self.cookie)
        try:
            csrf_token = cookie_parser["ct0"].value
        except KeyError:
            raise Exception("Twitter cookie not properly set")
        request_headers = {
            "authorization": AUTHORIZATION,
            "cookie": self.cookie,
            "x-csrf-token": csrf_token
        }
        variables = {
            "focalTweetId": str(tweet_id),
            "with_rux_injections": True,
            "includePromotedContent": True,
            "withCommunity": True,
            "withBirdwatchNotes": True,
            "withVoice": True
        }
        features = {
            "rweb_lists_timeline_redesign_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": False,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_media_download_video_enabled": False,
            "responsive_web_enhance_cards_enabled": False
        }
        request_url = f"{ROOT_URL}/i/api/graphql/q94uRCEn65LZThakYcPT6g/TweetDetail"

        request_body = {
            "variables": json.dumps(variables),
            "features": json.dumps(features)
        }
        request = requests.get(request_url, params=request_body, headers=request_headers)
        self._debug(f"Request responded with code {request.status_code}")
        self._debug(f"and the body {request.text}")
        return request

    def get_tweet_details(self, tweet_id):
        tweet_details = self._try_get_tweet_details(tweet_id)
        if tweet_details.status_code == 403:
            self._debug("Twitter prob screwing us over again...")
        if tweet_details.status_code != 200:
            self._debug("Trying to get tweet again...")
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

    def set_cookie(self, cookie):
        self.tm.cookie = cookie
