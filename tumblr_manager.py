import pytumblr
import re
from bs4 import BeautifulSoup
from response import Response

class TumblrManager:
    def __init__(self, consumer_key=None, consumer_secret=None, oauth_token=None, oauth_secret=None):
        self.initialized = False
        if not consumer_key or not consumer_secret or not oauth_token or not oauth_secret:
            return
        self.tumblr = pytumblr.TumblrRestClient(
            consumer_key,
            consumer_secret,
            oauth_token,
            oauth_secret
        )
        self.initialized = True

    def get_image_links(self, url):
        try:
            if not self.initialized:
                return {
                    "response": Response.FAILED,
                    "message": "Tumblr keys weren't provided"
                }
            poster, id = re.findall(r"tumblr.com\/(.*?)\/(\d+)", url)[0][:2]
            blog = self.tumblr.posts(poster, id=int(id))
            if "posts" not in blog:
                return {
                    "response": Response.REMOVED
                }
            posts = blog["posts"]
            post = [post for post in posts if post["id_string"] == id]
            post = post[0]
            if "photos" not in post:
                post = post["body"]
                post = BeautifulSoup(post, features="lxml")
                imgs = [img.attrs["srcset"] if "srcset" in img.attrs else img.attrs["src"] for img in post.find_all("img")]
                for i in range(len(imgs)):
                    img = imgs[i]
                    if "," in img:
                        srcset = [i.split() for i in img.split(", ")]
                        srcset = [[i[0], int(i[1][:-1])] for i in srcset]
                        srcset.sort(key=lambda x: x[-1])
                        imgs[i] = srcset[-1][0]
                    imgs[i] = imgs[i]
                vids = [vid.attrs["src"] for vid in post.find_all("source")]
                imgs.extend(vids)
            else:
                imgs = [photo["original_size"]["url"] for photo in post["photos"]]
            if not imgs:
                return {
                    "response": Response.FAILED,
                    "message": "Couldn't find anything in the post"
                }
            return {
                "response": Response.SUCCESS,
                "links": imgs
            }
        except Exception as e:
            return {
                "response": Response.FAILED,
                "message": repr(e)
            }
