# -*- coding: UTF-8 -*-

from flask import render_template, Blueprint, jsonify
from flask import request
from flask_login import login_required

import git_utils
from summer.models import Project, Group, User

__author__ = 'youpengfei'

mod = Blueprint('project', __name__)


@mod.route('/config/list', methods=['GET'])
@login_required
def project_config_list():
    kw = request.args.get('kw')
    if kw:
        projects = Project.query.filter(Project.name.like('%' + kw + '%')).all()
    else:
        kw = ''
        projects = Project.query.all()

    return render_template('project_config_list.html', projects=projects, kw=kw)


@mod.route('/config/edit/', methods=['GET'])
@login_required
def project_config_edit():
    project_id = int(request.args.get('projectId'))
    project = Project.query.filter_by(id=project_id).one()
    return render_template('project_config_edit.html', project=project)


@mod.route('/config/preview/', methods=['GET'])
@login_required
def project_review():
    project_id = int(request.args.get('projectId'))
    project = Project.query.filter_by(id=project_id).one()
    return render_template('project_preview.html', project=project)


@mod.route('/config/group/', methods=['GET'])
@login_required
def project_group():
    project_id = int(request.args.get('projectId'))
    groups = Group.query.filter_by(project_id=project_id).all()
    project = Project.query.filter_by(id=project_id).one()
    users = User.query.filter(User.id.in_(map(lambda x: x.user_id, groups))).all()
    all_users = User.query.all()
    return render_template('project_group.html', users=users, project=project, all_users=all_users)


@mod.route('/get-branch', methods=['GET'])
@login_required
def get_branch():
    project_id = int(request.args.get('projectId'))
    project = Project.query.filter_by(id=project_id).one()
    branch_list = git_utils.get_branch_list(project)
    return jsonify(data=branch_list,code=200)


@mod.route('/get-commit-history', methods=['GET'])
@login_required
def get_commit_list():
    project_id = int(request.args.get('projectId'))
    branch = request.args.get('branch')
    project = Project.query.filter_by(id=project_id).one()
    commit_list = git_utils.get_commit_list(project, branch=branch, count=10)
    return jsonify(data=commit_list,code=200)
