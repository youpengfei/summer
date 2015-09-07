# coding=utf-8
import subprocess

__author__ = 'youpengfei'
import os

from subprocess import call, Popen
from modules import Base, engine, db_session, Project, Server, Requirement
import time
from ssh_help import trans_data, command
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)

app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.route("/")
def index():
    all_requirement = db_session.query(Requirement).all()
    return render_template('index.html', all_requirement=all_requirement)


@app.route('/build')
def build_project():
    timestamp = str(int(time.time()))
    call(["rm", "-rf", "gpc"])
    call(['git', 'clone', 'git@git.letv.cn:cloud_vod_j/gpc.git'])
    call(['git', '-C', 'gpc', 'checkout', 'dev'])

    build_log = "build." + timestamp + ".log"

    call(['sh', 'build.sh'])
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


@app.route("/server/add", methods=['POST', 'GET'])
def server_add():
    if request.method == 'GET':
        return render_template("server_add.html")
    elif request.method == 'POST':
        ip = request.form['ip']
        port = request.form['port']
        passwd = request.form['passwd']
        key_file = request.form['key_file']
        deploy_dir = request.form['deploy_dir']
        server = Server(ip=ip, port=port, passwd=passwd, key_file=key_file, deploy_dir=deploy_dir)
        db_session.add(server)
        db_session.commit()
        return '成功'


@app.route("/server/list", methods=['POST', 'GET'])
def server_list():
    servers = db_session.query(Server).all()
    return render_template('server_list.html', server_list=servers)


@app.route("/project/add", methods=['POST', 'GET'])
def project_add():
    if request.method == 'GET':
        return render_template("project_add.html")
    elif request.method == 'POST':
        name = request.form['name']
        repo = request.form['repo']
        project_dir = request.form['project_dir']
        deploy_name = request.form['deploy_name']
        description = request.form['description']
        project = Project(name=name, repo=repo, project_dir=project_dir, deploy_name=deploy_name,
                          description=description)
        db_session.add(project)
        db_session.commit()
        return '成功'


@app.route("/project/list", methods=['GET'])
def project_list():
    projects = db_session.query(Project).all()
    return render_template('project_list.html', project_list=projects)


@app.route("/requirement/add", methods=['POST', 'GET'])
def requirement_add():
    if request.method == 'GET':
        projects = db_session.query(Project).all()
        servers = db_session.query(Server).all()
        return render_template("requirement_add.html", projects=projects, servers=servers)
    elif request.method == 'POST':
        branch_name = request.form['branch_name']
        servers = request.form['servers']
        server_list = ",".join(servers)
        project_id = request.form['project_id']
        requirement = Requirement(branch_name=branch_name, server_list=server_list, project_id=project_id)
        db_session.add(requirement)
        db_session.commit()
        return '成功'


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run('0.0.0.0')
