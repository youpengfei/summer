# -*- coding: UTF-8 -*-

from app import app, db
from app.models import Project, Requirement
from flask import request, render_template, redirect, jsonify, Blueprint

__author__ = 'youpengfei'

mod = Blueprint('project', __name__)


@mod.route("/add", methods=['POST', 'GET'])
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


@mod.route("/list", methods=['GET'])
def project_list():
    projects = Project.query.all()
    return render_template('project_list.html', project_list=projects, active="project")


@mod.route('/delete/<int:project_id>')
def project_delete(project_id):
    project = Project.query.filter_by(id=project_id).one()
    requirement_count = Requirement.query.filter_by(project_id=project_id).count()
    if requirement_count > 0:
        return jsonify(message='存在需求关联该项目,请先删除相关联的需求', code=500)

    if project:
        db.session.delete(project)
        db.session.commit()
    return jsonify(message='删除成功', code=200)
