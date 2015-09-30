# encoding:utf-8
# !/usr/bin/python
from app import app

import os, subprocess

# 加载依赖
subprocess.call(['virtualenv', 'summer'])
subprocess.call([os.path.join('summer', 'bin', 'pip'), 'install', '-r', 'requirements.txt'])

# 初始化数据库

app.db.create_all()
