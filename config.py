# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'instance', 'casa_leones.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Bump this whenever any static asset (CSS/JS) changes, to force browser reload
    VERSION = '1.4.9'