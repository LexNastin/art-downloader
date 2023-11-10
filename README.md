# Art Downloader

A nice little web-based downloader and viewer for art you find on the internet. It's capable of automatically adding posts from Tumblr, Reddit, Twitter, and Instagram (using their unofficial APIs, except Tumblr - you gotta get free API keys for that), and generating thumbnails for them so for every piece of art you save, you get a preview. Also supports tagging your art so you can find it easily later.

## Usage

### Docker

To begin, clone this repo:
```sh
git clone https://github.com/ArchGryphon9362/art-downloader
```

Make sure you have Docker installed. Edit ports in `docker-compose.yml` as needed. You may set the SECRET_KEY variable to something very secure (you may use `python -c 'import secrets; print(secrets.token_hex())'` in the terminal to generate it) if you wish for logins to persist whenever the container restarts.

Now, to start the container, simply run the following:

```sh
docker compose up -d --build
```

### Manual

To begin, clone this repo:
```sh
git clone https://github.com/ArchGryphon9362/art-downloader
```

Install the requirements
```sh
pip3 install -r requirements.txt
```

And run the program
```sh
python3 main.py
```

From there everything should make sense (hopefully). Be sure to report any bugs!

## Making Tumblr Work

Go to the settings page, you should see fields to set your Tumblr tokens. Read the [Create a client](https://github.com/tumblr/pytumblr#create-a-client) section of the PyTumblr library, which lists methods to obtain those tokens.

This method is deprecated and will be removed at 2.0.0 (if that ever happens haha). Setting the following 4 environment variables will work for now, but will only work if their respective tokens are not currently set in the settings.
```env
CONSUMER_KEY = <consumer key>
CONSUMER_SECRET = <consumer secret>
OAUTH_TOKEN = <oauth token>
OAUTH_SECRET = <oauth secret>
```

## Making Twitter Work

Go to Twitter and login (you can create an account for the sole purpose of this program). Now open the F12 menu and go to the `Network` tab. Refresh the page, and look at the first request. Go to the `Headers` tab on that request, and scroll down until you see the `Cookie` header. Copy the cookie, and go to the settings of the Art Downloader. There you should find a Twitter Cookie setting. Paste your cookie there and save. Twitter uploads should now work :D. I'm not sure how long these last, so if something's not working after a little while, try repeating this step.

## Supporting The Development of This Tool

First of all, if you like the art hosted on any of the instances I host, DO NOT donate to this tool. Any such donations WILL BE refunded. Rather, support the respective artists directly. Find them by going to the sources of the art you find, and looking for a donate/commission link somewhere on their page. I am not in any way trying to steal what should be going to them. Now, if you actually came here to support me in the development of Art Downloader, you can either help by finding issues and/or submitting useful pull requests, or if you really want to, by clicking on the"Donate" button at the top of this GitHub repo, where you can find [my Ko-fi page](https://ko-fi.com/lexnastin). Thanks to everyone for absolutely any type of support, as this is just a hobby project that I maintain for personal use in my free time.
