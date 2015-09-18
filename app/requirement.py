from app import app, db
from app.models import Project, Server, Requirement
from flask import request, render_template, redirect

__author__ = 'youpengfei'


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
