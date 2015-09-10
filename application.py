# coding=utf-8
import subprocess

__author__ = 'youpengfei'
import os

from subprocess import call, Popen
from modules import Base, engine, db_session, Project, Server, Requirement
import time
from ssh_help import trans_data, command, command_with_result
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)

app.config.from_object(__name__)

MAVEN_BIN = 'mvn'


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.route("/")
def index():
    all_requirement = db_session.query(Requirement).all()
    for requirement in all_requirement:
        servers = db_session.query(Server).filter(
            Server.id.in_(requirement.server_list.split(","))).all()
        project = db_session.query(Project).filter_by(id=requirement.project_id).one()
        requirement.server_ip_list = ",".join([x.ip for x in servers])
        requirement.project_name = project.name

    return render_template('index.html', all_requirement=all_requirement)


@app.route('/build/<int:id>')
def build_project(id):
    timestamp = str(int(time.time()))
    requirement = db_session.query(Requirement).filter_by(id=id).one()
    project = db_session.query(Project).filter_by(id=requirement.project_id).one()
    call(["rm", "-rf", project.project_dir])
    call(['git', 'clone', '-b', requirement.branch_name, project.repo])
    maven_result = Popen(
        [MAVEN_BIN, '-U', 'clean', 'package', '-Dmaven.test.skip=true', '-s', '%s/settings.xml' % project.project_dir,
         '-f', project.project_dir], stdout=subprocess.PIPE)
    build_log = 'build.%s.log' % timestamp
    file = open(build_log, 'w')
    file.write(maven_result.stdout.read())
    file.close()

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
    requirement = db_session.query(Requirement).filter_by(id=id).one()
    project = db_session.query(Project).filter_by(id=requirement.project_id).one()
    server_ids = requirement.server_list.split(',')
    package_name = project.deploy_name
    result = ""
    for server_id in server_ids:
        server = db_session.query(Server).filter_by(id=server_id).one()
        ssh_key = server.key_file
        trans_data(server.ip, ssh_key, "%s/%s" % (server.deploy_dir, package_name),
                   '%s/target/%s' % (project.project_dir, package_name))

    return result


@app.route('/restart/<int:id>')
def restart(id):
    requirement = db_session.query(Requirement).filter_by(id=id).one()
    server_ids = requirement.server_list.split(',')
    result = ""
    for server_id in server_ids:
        server = db_session.query(Server).filter_by(id=server_id).one()
        ssh_key = server.key_file
        command(server.ip, ssh_key, 'cd %s && ./start_for_summer.sh' % server.deploy_dir)
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
        servers = request.form.getlist('servers')
        server_list = ",".join(servers)
        project_id = request.form['project_id']
        requirement = Requirement(branch_name=branch_name, server_list=server_list, project_id=project_id)
        db_session.add(requirement)
        db_session.commit()
        return '成功'


@app.route("/server/log/<int:id>")
def logs(id):
    server = db_session.query(Server).filter_by(id=id).one()
    result = command_with_result(server.ip, server.key_file,
                                 'tail -n200 %s/%s ' % (server.deploy_dir, 'logs/gpc-j.log'))
    print result
    return render_template('project_log.html', result=result)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(host='0.0.0.0', debug=True)
