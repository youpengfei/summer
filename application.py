# coding=utf-8
__author__ = 'youpengfei'

import os
import time
from ssh_help import trans_data, command
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


# configuration
DATABASE = '/tmp/summer.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)

app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


hosts = {54: {"host": "10.154.29.54", "key_filename": ""},
         53: {"host": "10.154.29.53", "key_filename": ""},
         }


@app.route("/")
def index():
    all_project = get_project()
    return render_template('index.html', projects=all_project)


@app.route('/build')
def build_project():
    timestamp = str(int(time.time()))
    os.system("rm -rf gpc")
    os.system('git clone git@git.letv.cn:cloud_vod_j/gpc.git')
    os.system('cd gpc && git checkout dev')
    build_log = "build." + timestamp + ".log"
    os.system('mvn  -U clean package -Dmaven.test.skip=true  -s gpc/settings.xml -f gpc >>' + build_log)
    return timestamp


@app.route('/build/log/<timestamp>')
def build_log(timestamp=None):
    log_name = 'build.' + timestamp + '.log'
    file_object = open(log_name)
    try:
        list_of_all_the_lines = file_object.readlines()
    finally:
        file_object.close()
    return render_template("build_log.html", logs=list_of_all_the_lines)


@app.route('/deploy/<int:id>')
def deploy(id):
    if id is None:
        return "id不能为空"
    hostname = hosts[id]['host']
    key_filename = hosts[id]['key_filename']
    trans_data(hostname, key_filename, '/home/tomcat/gpc/', 'gpc/target/')
    return "发布成功"


@app.route('/restart/<int:id>')
def restart(id):
    if id is None:
        return "id不能为空"
    hostname = hosts[id]['host']
    key_filename = hosts[id]['key_filename']
    if command(hostname, key_filename, 'cd /home/tomcat/gpc && ./start_for_summer.sh'):
        return "重启成功"
    else:
        return "重启失败"


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()


def get_project():
    cur = g.db.execute('select id, name,repo,project_dir,deploy_name,description from project order by id desc')
    return [dict(id=row[0], name=row[1], repo=row[2], project_dir=row[3], deploy_name=row[4], description=row[5]) for
            row in cur.fetchall()]


if __name__ == '__main__':
    app.run('0.0.0.0')
