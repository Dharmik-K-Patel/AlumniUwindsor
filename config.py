import os

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://flask_user:mahir123@localhost/obituary_data"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "a3f5b6c2d9e8f1a4b7c6d2e9f3a5b4c1")  # Fallback for development
