from flask import Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .media_manager import MediaManager

load_dotenv()
SCRIPT_DIR = os.getcwd()

DATA_DIR = os.path.join(SCRIPT_DIR, "data")
MEDIA_DIR = os.path.join(DATA_DIR, "media")
TEMP_DIR = os.path.join("/tmp", "art-downloader")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

db = SQLAlchemy()
media_manager = MediaManager()

def create_app():
    # create app
    app = Flask(__name__)

    # setup secret key, db directory, and auto reload templates
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or os.urandom(32).hex()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(DATA_DIR, "data.db")
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    # initialize db with app context
    db.init_app(app)
    migrate = Migrate(app, db)

    # create db
    from .models import User, Post, Setting
    with app.app_context():
        db.create_all()

    # setup global jinja variables
    from .settings import get_setting, set_setting
    @app.context_processor
    def inject_globals():
        return dict(app_name=get_setting("app_name", "Art Downloader"), github_button=int(get_setting("github_button", "0")))

    # setup API tokens
    with app.app_context():
        # tumblr token
        tumblr_consumer_key = get_setting("tumblr_consumer_key", "") or os.getenv("CONSUMER_KEY") or ""
        tumblr_consumer_secret = get_setting("tumblr_consumer_secret", "") or os.getenv("CONSUMER_SECRET") or ""
        tumblr_oauth_token = get_setting("tumblr_oauth_token", "") or os.getenv("OAUTH_TOKEN") or ""
        tumblr_oauth_secret = get_setting("tumblr_oauth_secret", "") or os.getenv("OAUTH_SECRET") or ""

        set_setting("tumblr_consumer_key", tumblr_consumer_key)
        set_setting("tumblr_consumer_secret", tumblr_consumer_secret)
        set_setting("tumblr_oauth_token", tumblr_oauth_token)
        set_setting("tumblr_oauth_secret", tumblr_oauth_secret)

        media_manager.tumblr_manager.set_token(
            consumer_key=tumblr_consumer_key,
            consumer_secret=tumblr_consumer_secret,
            oauth_secret=tumblr_oauth_secret,
            oauth_token=tumblr_oauth_token
        )

        # twitter cookie
        twitter_cookie = get_setting("twitter_cookie", "")
        media_manager.twitter_manager.set_cookie(twitter_cookie)

    # setup login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = ''
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # register blueprints
    from .auth import auth
    app.register_blueprint(auth)

    from .main import main
    app.register_blueprint(main)
    
    return app
