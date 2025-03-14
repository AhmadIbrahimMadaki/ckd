from django import db
from app import create_app
from flask_migrate import Migrate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .app.routes.auth import auth_bp

app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.register_blueprint(auth_bp)
    app.run(debug=True)
