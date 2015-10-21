from .. import db
from flask_login import login_required
from ..models import Project, Server, Requirement
from flask import request, render_template, redirect, Blueprint

__author__ = 'youpengfei'

mod = Blueprint('requirement', __name__)


@mod.route("/add", methods=['POST', 'GET'])
@login_required
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


@mod.route("/modify/<int:requirement_id>", methods=['POST', 'GET'])
@login_required
def requirement_modify(requirement_id):
    if request.method == 'GET':
        projects = Project.query.all()
        servers = Server.query.all()
        requirement = Requirement.query.filter_by(id=requirement_id).one()
        requirement_servers = Server.query.filter(Server.id.in_(requirement.server_list.split(","))).all()
        requirement.server_ip_list = [x.ip for x in servers]
        return render_template("requirement_modify.html",
                               projects=projects,
                               servers=servers,
                               requirement=requirement)
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
