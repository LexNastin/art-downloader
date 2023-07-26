# Art Downloader

A nice little web-based downloader and viewer for art you find on the internet. It's capable of automatically adding posts from Tumblr, Reddit, Twitter, and Instagram (using their unofficial APIs, except Tumblr - you gotta get free API keys for that), and generating thumbnails for them so for every piece of art you save, you get a preview. Also supports tagging your art so you can find it easily later.

## Usage

### Docker

Make sure you have Docker installed. Edit ports in `docker-compose.yml` and environment variables as needed. You may set the SECRET_KEY variable to something very secure if you wish for logins to persist whenever the container restarts.

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

For Tumblr to work, you must set the following 4 environment variables. Read the [Create a client](https://github.com/tumblr/pytumblr#create-a-client) section of the PyTumblr library, which explains methods to obtain those tokens.

```env
CONSUMER_KEY = <consumer key>
CONSUMER_SECRET = <consumer secret>
OAUTH_TOKEN = <oauth token>
OAUTH_SECRET = <oauth secret>
```

## Making Twitter Work

Go to Twitter and login (you can create an account for the sole purpose of this program). Now open the F12 menu and go to the `Network` tab. Refresh the page, and look at the first request. Go to the `Headers` tab on that request, and scroll down until you see the `Cookie` header. Copy the cookie, and go to the settings of the Art Downloader. There you should find a Twitter Cookie setting. Paste your cookie there and save. Twitter uploads should now work :D. I'm not sure how long these last, so if something's not working after a little while, try repeating this step.
