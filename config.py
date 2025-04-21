# config.py
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///casa_leones.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Bump this whenever any static asset (CSS/JS) changes, to force browser reload
    VERSION = '1.0.3'