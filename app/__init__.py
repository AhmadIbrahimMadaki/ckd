from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize the database
db = SQLAlchemy()

# Initialize Flask-Migrate
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)  # Initialize SQLAlchemy
    migrate.init_app(app, db)  # Initialize Flask-Migrate with your app and db

    return app
