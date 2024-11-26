from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
from .routes import main

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.secret_key = "4b8e3b92e6b7c8d943dab21cf9823a6f9e8c4dbcf7e5b4caff812cd75f77bdf8"  # Replace with your generated key
    app.register_blueprint(main)
    return app
