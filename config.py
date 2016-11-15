# -*- coding: UTF-8 -*-

import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format('summer', 'summer', '127.0.0.1', 3306, 'summer')

# 'mysql://summer:summer@127.0.0.1/summer'

SQLALCHEMY_ECHO = True
PASSWORD_SALT = "you-will-never-guess"
