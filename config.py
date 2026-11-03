import os
from extensions import db, bcrypt, ma

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "development-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///notes.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False