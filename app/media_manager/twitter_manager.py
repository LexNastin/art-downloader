import requests
from http.cookies import SimpleCookie
import json
import re
from enum import Enum
from .response import Response

ROOT_URL = "https://x.com"
AUTHORIZATION = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

class Twitter:
    def __init__(self, log_level=1):
        self.log_level = log_level
        self.cookie = ""
        self.user_agent = ""

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
            "content-type": "application/json",
            "cookie": self.cookie,
            "x-csrf-token": csrf_token
        }
        if self.user_agent != "":
            request_headers["user-agent"] = self.user_agent

        variables = {
            "focalTweetId": str(tweet_id),
            "with_rux_injections": False,
            "rankingMode": "Relevance",
            "includePromotedContent": True,
            "withCommunity": True,
            "withBirdwatchNotes": True,
            "withVoice": True
        }
        features = {
            "rweb_video_screen_enabled": False,
            "payments_enabled": False,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "responsive_web_profile_redirect_enabled": False,
            "rweb_tipjar_consumption_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "premium_content_api_read_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
            "responsive_web_grok_analyze_post_followups_enabled": True,
            "responsive_web_jetfuel_frame": True,
            "responsive_web_grok_share_attachment_enabled": True,
            "articles_preview_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "responsive_web_grok_show_grok_translated_post": False,
            "responsive_web_grok_analysis_button_from_backend": True,
            "creator_subscriptions_quote_tweet_preview_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_grok_image_annotation_enabled": True,
            "responsive_web_grok_imagine_annotation_enabled": True,
            "responsive_web_grok_community_note_auto_translation_is_enabled": False,
            "responsive_web_enhance_cards_enabled": False
        }

        request_url = f"{ROOT_URL}/i/api/graphql/YVyS4SfwYW7Uw5qwy0mQCA/TweetDetail"

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

class TwitterParser:
    class TweetItem:
        class DisplayType(Enum):
            TWEET = 0
            SELF_THREAD = 1

            OTHER = -1

            @classmethod
            def from_str(cls, display_type):
                if display_type == "Tweet":
                    return cls.TWEET
                if display_type == "SelfThread":
                    return cls.SELF_THREAD

                return cls.OTHER

        def __init__(self, content):
            # some more modern tweets (i think it's only the advertisement ones lol)
            if "tweet" in content["tweet_results"]["result"]:
                content["tweet_results"]["result"] = content["tweet_results"]["result"]["tweet"]

            tweet = content["tweet_results"]["result"]["legacy"]

            self.tweet_id = tweet["id_str"]
            self.display_type = self.DisplayType.from_str(content["tweetDisplayType"])
            self.quote_url = None
            self.incomplete = False
            self.media_links = []

            if "quoted_status_permalink" in tweet:
                self.quote_url = tweet["quoted_status_permalink"]["expanded"]

            media_entities = []
            if "extended_entities" in tweet:
                media_entities = tweet["extended_entities"]["media"]

            for entry in media_entities:
                if entry["type"] == "photo":
                    self.add_media(entry["media_url_https"] + "?format=png&name=4096x4096")
                elif entry["type"] in ["video", "animated_gif"]:
                    videos = entry["video_info"]["variants"]
                    videos.sort(key=lambda x: x["bitrate"] if "bitrate" in x else 0)
                    video_url = videos[-1]["url"]
                    self.add_media(video_url)
                else:
                    self.incomplete = True
                    continue

        def add_media(self, link):
            self.media_links.append(link)

    class TombstoneItem:
        pass

    class TimelineModule:
        def __init__(self):
            self.items = []

        def add_item(self, item):
            self.items.append(item)

    class Timeline:
        def __init__(self):
            self.entries = []

        # entry should be either a module, or one of the item types
        def add_entry(self, entry):
            self.entries.append(entry)

    def __init__(self):
        self.timeline = self.Timeline()

    @classmethod
    def _parse_timeline_item(cls, item):
        content = item["itemContent"]
        itemType = content["itemType"]

        # regular tweet
        if itemType == "TimelineTweet":
            if "result" not in content["tweet_results"]:
                # idk if all dead tweet look like this, or only ones that were deleted less recently (and hence fully deleted from their systems), but a tweet item with no results is effectively a tombstone item.
                return cls.TombstoneItem()
            if "tombstone" in content["tweet_results"]["result"]:
                return cls.TombstoneItem()
            return cls.TweetItem(content)

        # dead tweet
        if itemType == "TimelineTombstone":
            return cls.TombstoneItem()

        return None

    @classmethod
    def _parse_timeline_entry(cls, entry):
        content = entry["content"]
        entryType = content["entryType"]

        # main item
        if entryType == "TimelineTimelineItem":
            return cls._parse_timeline_item(content)

        # module (group of items)
        if entryType == "TimelineTimelineModule":
            module = cls.TimelineModule()

            reply_items = content["items"]
            for item in reply_items:
                parsed_item = cls._parse_timeline_item(item["item"])
                if parsed_item != None:
                    module.add_item(parsed_item)

            return module

        return None

    def _parse_instruction(self, instruction):
        instrType = instruction["type"]

        if instrType == "TimelineAddEntries":
            for entry in instruction["entries"]:
                parsed_entry = self._parse_timeline_entry(entry)
                if parsed_entry != None:
                    self.timeline.add_entry(parsed_entry)

    def parse_tweet_details(self, tweet_details):
        instructions = tweet_details["data"]["threaded_conversation_with_injections_v2"]["instructions"]
        for instruction in instructions:
            self._parse_instruction(instruction)

class TwitterManager:
    def __init__(self):
        self.tm = Twitter(log_level=0)

    def get_image_links(self, url):
        try:
            tweet_id = re.findall(r"/status/(\d+)", url)[0]
            tweeter = re.findall(r"(?:twitter|x).com/(.*?)/status/\d+", url)[0]
            tweet_details = self.tm.get_tweet_details(tweet_id)
            links = []

            if not tweet_details:
                return {
                    "response": Response.REMOVED
                }

            twitter_parser = TwitterParser()
            twitter_parser.parse_tweet_details(tweet_details)
            entries = twitter_parser.timeline.entries

            response_type = Response.SUCCESS

            # parse root item
            root_item = entries[0]
            if type(root_item) is TwitterParser.TombstoneItem:
                return {
                    "response": Response.REMOVED
                }
            if type(root_item) is TwitterParser.TweetItem:
                links.extend(root_item.media_links)
                if root_item.incomplete:
                    response_type = Response.INCOMPLETE

            # parse self thread
            for entry in entries[1:]:
                if type(entry) is TwitterParser.TimelineModule:
                    found_self_thread = False

                    for item in entry.items:
                        if type(item) is TwitterParser.TweetItem:
                            if item.display_type == TwitterParser.TweetItem.DisplayType.SELF_THREAD:
                                links.extend(item.media_links)
                                if item.incomplete:
                                    response_type = Response.INCOMPLETE

                    if found_self_thread:
                        break

            if not links and type(root_item) is TwitterParser.TweetItem:
                quote_url = root_item.quote_url
                if quote_url != None:
                    return self.get_image_links(quote_url)

            if not links:
                return {
                    "response": Response.FAILED,
                    "message": "Not a media post!"
                }

            return {
                "response": response_type,
                "links": links,
                "url": url.split("?")[0]
            }
        except Exception as e:
            return {
                "response": Response.FAILED,
                "message": repr(e)
            }

    def set_cookie(self, cookie):
        self.tm.cookie = cookie

    def set_user_agent(self, user_agent):
        self.tm.user_agent = user_agent
