# coding=utf-8
import os
import time
from ssh_help import trans_data

__author__ = 'youpengfei'

from flask import Flask, render_template

app = Flask(__name__)

mavenBin = '/usr/local/Cellar/maven/3.3.3/libexec/bin/'

hosts = {54: {"host": "10.154.29.54", "key_filename": ""},
         53: {"host": "10.154.29.53", "key_filename": ""},
         }


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/build')
def build_project():
    timestamp = str(int(time.time()))
    os.system("rm -rf gpc")
    os.system('git clone git@git.letv.cn:cloud_vod_j/gpc.git')
    os.system('cd gpc && git checkout dev')
    build_log = "build." + timestamp + ".log"
    os.system(mavenBin + 'mvn  -U clean package -Dmaven.test.skip=true  -s gpc/settings.xml -f gpc >>' + build_log)
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
    restart(hostname, key_filename, '')
    return "发布成功"


if __name__ == '__main__':
    app.run()
