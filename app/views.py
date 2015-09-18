# -*- coding: UTF-8 -*-
import time
from subprocess import call

from app import app
from app.models import Project, Server, Requirement
from flask.ext.login import login_required
from ssh_help import trans_data, command
from flask import request, render_template

MAVEN_BIN = 'mvn'


@app.route("/")
@login_required
def index():
    all_requirement = Requirement.query.all()
    for requirement in all_requirement:
        servers = Server.query.filter(Server.id.in_(requirement.server_list.split(","))).all()
        project = Project.query.filter_by(id=requirement.project_id).one()
        requirement.server_ip_list = [x.ip for x in servers]
        requirement.project_name = project.name

    return render_template('index.html', all_requirement=all_requirement)


@app.route('/build/<int:id>')
def build_project(id):
    timestamp = str(int(time.time()))
    requirement = Requirement.query.filter_by(id=id).one()
    project = Project.query.filter_by(id=requirement.project_id).one()
    call(["rm", "-rf", project.project_dir])
    call(['git', 'clone', '-b', requirement.branch_name, project.repo])
    call([MAVEN_BIN, '-U', 'clean', 'package', '-Dmaven.test.skip=true', '-s', '%s/settings.xml' % project.project_dir,
          '-f', project.project_dir])

    return timestamp


@app.route('/deploy/<int:id>')
def deploy(id):
    requirement = Requirement.query.filter_by(id=id).one()
    project = Project.query.filter_by(id=requirement.project_id).one()
    server_ids = requirement.server_list.split(',')
    package_name = project.deploy_name
    result = ""
    for server_id in server_ids:
        server = Server.query.filter_by(id=server_id).one()
        ssh_key = server.key_file
        trans_data(server.ip, ssh_key, "%s/%s" % (project.deploy_dir, package_name),
                   '%s/target/%s' % (project.project_dir, package_name))

    return result


@app.route('/init/<int:id>')
def init_project(id):
    requirement = Requirement.query.filter_by(id=id).one()
    project = Project.query.filter_by(id=requirement.project_id).one()
    server_ids = requirement.server_list.split(',')
    result = ""
    for server_id in server_ids:
        server = Server.query.filter_by(id=server_id).one()
        ssh_key = server.key_file

        command(server.ip, ssh_key, 'mkdir -p %s' % project.deploy_dir)

        command(server.ip, ssh_key, 'touch   %s/%s' % (project.deploy_dir, 'start_for_summer.sh'))
        command(server.ip, ssh_key,
                'echo  "%s" > %s/%s' % (project.start_sh.replace('$', '\$'), project.deploy_dir, 'start_for_summer.sh'))
        command(server.ip, ssh_key, 'chmod u+x   %s/%s' % (project.deploy_dir, 'start_for_summer.sh'))

        command(server.ip, ssh_key, 'touch   %s/%s' % (project.deploy_dir, 'stop.sh'))
        command(server.ip, ssh_key,
                'echo  "%s" >%s/%s' % (project.stop_sh.replace('$', '\$'), project.deploy_dir, 'stop.sh'))
        command(server.ip, ssh_key, 'chmod u+x   %s/%s' % (project.deploy_dir, 'stop.sh'))

    return result


@app.route('/restart/<int:id>')
def restart(id):
    requirement = Requirement.query.filter_by(id=id).one()
    server_ids = requirement.server_list.split(',')
    project = Project.query.filter_by(id=requirement.project_id).one()
    result = ""
    for server_id in server_ids:
        server = Server.query.filter_by(id=server_id).one()
        ssh_key = server.key_file
        command(server.ip, ssh_key, 'cd %s && ./start_for_summer.sh' % project.deploy_dir)
    return result


@app.route("/config/start", methods=['POST', 'GET'])
def start_config():
    if request.method == 'GET':
        servers = Server.query.all()
        return render_template('config.html', servers=servers)
    elif request.method == 'POST':
        file = open('start_for_summer.sh', 'w')
        file.write(request.form['sh'])
        file.close()
        servers = request.form.getlist('servers')
        for server_id in servers:
            server = Server.query.filter_by(id=server_id).one()
            ssh_key = server.key_file
            trans_data(server.ip, ssh_key, "%s/" % server.deploy_dir, 'start_for_summer.sh')
        return "成功"
