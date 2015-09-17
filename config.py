import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:nishishi@10.154.29.54/summer'
SQLALCHEMY_ECHO = True
