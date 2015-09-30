# -*- coding: UTF-8 -*-
import time

from .. import app
from ..models import Project, Server, Requirement
from flask.ext.login import login_required
from plumbum.machines.paramiko_machine import ParamikoMachine
from flask import render_template, Blueprint
from plumbum import local

mod = Blueprint('main', __name__)


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
    local['rm']["-rf", project.project_dir]()
    local['git']['clone', '-b', requirement.branch_name, project.repo]()
    local['mvn'][
        '-U', 'clean', 'package', '-Dmaven.test.skip=true', '-s', '%s/settings.xml' % project.project_dir, '-f', project.project_dir]()

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
        rem = ParamikoMachine(host=server.ip, keyfile=server.key_file, user='tomcat')
        rem.upload('%s/target/%s' % (project.project_dir, package_name), "%s/%s" % (project.deploy_dir, package_name))
        rem.close()
    return result


@app.route('/init/<int:id>')
def init_project(id):
    requirement = Requirement.query.filter_by(id=id).one()
    project = Project.query.filter_by(id=requirement.project_id).one()
    server_ids = requirement.server_list.split(',')
    result = ""
    for server_id in server_ids:
        server = Server.query.filter_by(id=server_id).one()
        rem = ParamikoMachine(host=server.ip, keyfile=server.key_file, user='tomcat')
        rem.path(project.deploy_dir).mkdir()
        start_sh_path = rem.path('%s/%s' % (project.deploy_dir, 'start_for_summer.sh'))
        start_sh_path.write(project.start_sh)
        # 国外程序员也不靠谱啊 写个8进制查了好久
        start_sh_path.chmod(0755)
        stop_sh_path = rem.path('%s/%s' % (project.deploy_dir, 'stop.sh'))
        stop_sh_path.write(project.stop_sh)
        # 国外程序员也不靠谱啊 写个8进制查了好久
        stop_sh_path.chmod(0755)
        rem.close()
    return result


@app.route('/restart/<int:id>')
def restart(id):
    requirement = Requirement.query.filter_by(id=id).one()
    server_ids = requirement.server_list.split(',')
    project = Project.query.filter_by(id=requirement.project_id).one()
    result = ""
    for server_id in server_ids:
        server = Server.query.filter_by(id=server_id).one()
        rem = ParamikoMachine(host=server.ip, keyfile=server.key_file, user='tomcat')
        rem['%s/start_for_summer.sh' % project.deploy_dir]()
        rem.close()
    return result
