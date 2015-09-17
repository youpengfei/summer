import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
SQLALCHEMY_DATABASE_URI = 'mysql://root:nishishi@127.0.0.1/summer'
SQLALCHEMY_ECHO = True
