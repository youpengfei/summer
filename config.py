import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'summer.db')
