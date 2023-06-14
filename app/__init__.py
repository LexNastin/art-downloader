from flask import Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from app.media_manager import MediaManager
from flask_login import LoginManager

load_dotenv()
SCRIPT_DIR = os.getcwd()
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

db = SQLAlchemy()
# media_manager = MediaManager()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or os.urandom(32).hex()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(DATA_DIR, "data.db")
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    db.init_app(app)

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = ''
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth
    app.register_blueprint(auth)

    from .main import main
    app.register_blueprint(main)
    
    return app
