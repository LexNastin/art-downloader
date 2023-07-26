# Art Downloader

A nice little web-based downloader and viewer for art you find on the internet. It's capable of automatically adding posts from Tumblr, Reddit, Twitter, and Instagram (using their unofficial APIs, except Tumblr - you gotta get free API keys for that), and generating thumbnails for them so for every piece of art you save, you get a preview. Also supports tagging your art so you can find it easily later.

## Usage

### Docker

TBA

### Manual / Development

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
flask run
```

From there everything should make sense (hopefully). Be sure to report any bugs!

For Tumblr to work, you must set the following 4 environment variables (you can create a `.env` file on the repo root directory to use them). Read the [Create a client](https://github.com/tumblr/pytumblr#create-a-client) section of the PyTumblr library, which explains methods to obtain those tokens.

```env
CONSUMER_KEY = <consumer key>
CONSUMER_SECRET = <consumer secret>
OAUTH_TOKEN = <oauth token>
OAUTH_SECRET = <oauth secret>
```
