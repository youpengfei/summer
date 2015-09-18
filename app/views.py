# -*- coding: UTF-8 -*-
import time
import subprocess
from subprocess import call, Popen

from app import db, app, login_manager
from app.models import Project, Server, Requirement, User
from flask.ext.login import login_user, login_required
from ssh_help import trans_data, command, command_with_result
from flask import request, render_template, jsonify, flash, url_for
from werkzeug.utils import redirect
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField

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


@app.route("/server/add", methods=['POST', 'GET'])
def server_add():
    if request.method == 'GET':
        return render_template("server_add.html", active="server")
    elif request.method == 'POST':
        ip = request.form['ip']
        port = request.form['port']
        passwd = request.form['passwd']
        key_file = request.form['key_file']
        server = Server(ip=ip, port=port, passwd=passwd, key_file=key_file)
        db.session.add(server)
        db.session.commit()
        return redirect('/server/list')


@app.route("/server/list", methods=['POST', 'GET'])
def server_list():
    servers = Server.query.all()
    return render_template('server_list.html', server_list=servers, active="server")


@app.route("/project/add", methods=['POST', 'GET'])
def project_add():
    if request.method == 'GET':
        return render_template("project_add.html", active="project")
    elif request.method == 'POST':
        name = request.form['name']
        repo = request.form['repo']
        project_dir = request.form['project_dir']
        deploy_name = request.form['deploy_name']
        description = request.form['description']
        deploy_dir = request.form['deploy_dir']
        package_type = request.form['package_type']
        project = Project(name=name,
                          repo=repo,
                          project_dir=project_dir,
                          deploy_name=deploy_name,
                          deploy_dir=deploy_dir,
                          package_type=package_type,
                          description=description)
        db.session.add(project)
        db.session.commit()
        return redirect('/project/list')


@app.route("/project/list", methods=['GET'])
def project_list():
    projects = Project.query.all()
    return render_template('project_list.html', project_list=projects, active="project")


@app.route("/requirement/add", methods=['POST', 'GET'])
def requirement_add():
    if request.method == 'GET':
        projects = Project.query.all()
        servers = Server.query.all()
        return render_template("requirement_add.html", projects=projects, servers=servers)
    elif request.method == 'POST':
        branch_name = request.form['branch_name']
        servers = request.form.getlist('servers')
        name = request.form['name']
        server_list = ",".join(servers)
        project_id = request.form['project_id']
        requirement = Requirement(branch_name=branch_name, server_list=server_list, project_id=project_id, name=name)
        db.session.add(requirement)
        db.session.commit()
        return redirect('/')


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


@app.route("/server/log/<int:server_id>")
def logs(server_id):
    server = Server.query.filter_by(id=server_id).one()
    result = command_with_result(server.ip, server.key_file,
                                 'tail -n200 %s/%s ' % (server.deploy_dir, 'logs/gpc-j.log'))
    print result
    return render_template('project_log.html', result=result)


@app.route('/project/delete/<int:project_id>')
def project_delete(project_id):
    project = Project.query.filter_by(id=project_id).one()
    requirement_count = Requirement.query.filter_by(project_id=project_id).count()
    if requirement_count > 0:
        return jsonify(message='存在需求关联该项目,请先删除相关联的需求', code=500)

    if project:
        db.session.delete(project)
        db.session.commit()
    return jsonify(message='删除成功', code=200)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = LoginForm()
        user = User.query.filter_by(email=form.email.data).one()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect('/')

    return render_template('login.html')


@login_manager.user_loader
def get_user(ident):
    return User.query.get(int(ident))


class LoginForm(Form):
    email = StringField('email')
    password = PasswordField('password')
    submit = SubmitField()
