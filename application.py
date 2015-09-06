# coding=utf-8
from db_help import save

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


@app.route('/deploy')
def deploy():
    package_name = 'gpc-0.0.1-SNAPSHOT.jar'
    ssh_key = '/home/tomcat/.ssh/id_rsa'
    result = ""
    if trans_data('10.154.29.54', ssh_key, '/home/tomcat/gpc/%s' % package_name, 'gpc/target/%s' % package_name):
        result = "54发布成功"
    if trans_data('10.154.29.53', ssh_key, '/home/tomcat/gpc/%s' % package_name, 'gpc/target/%s' % package_name):
        result += "\r53发布成功"
    return result


@app.route('/restart')
def restart():
    result = ""
    if command('10.154.29.54', '/home/tomcat/.ssh/id_rsa', 'cd /home/tomcat/gpc && ./start_for_summer.sh'):
        result = "54发布成功"
    if command('10.154.29.53', '/home/tomcat/.ssh/id_rsa', 'cd /home/tomcat/gpc && ./start_for_summer.sh'):
        result += "53发布成功"
    return result


@app.route("/add_server", methods=['POST', 'GET'])
def add_server():
    if request.method == 'GET':
        return render_template("add_server.html")
    elif request.method == 'POST':
        ip = request.form['ip']
        port = request.form['port']
        passwd = request.form['passwd']
        key_file = request.form['key_file']
        deploy_dir = request.form['deploy_dir']
        sql = '''insert into server(ip,port,passwd,key_file,deploy_dir) values(%s,%s,%s,%s,%s)'''
        save(g.db, sql, (ip, port, passwd, key_file, deploy_dir))
        return '成功'


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
