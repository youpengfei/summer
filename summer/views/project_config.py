# -*- coding: UTF-8 -*-

from flask import render_template, Blueprint
from flask import request
from flask_login import login_required

from summer.models import Project, Group, User

__author__ = 'youpengfei'

mod = Blueprint('project_config', __name__)


@mod.route('/list', methods=['GET'])
@login_required
def project_config_list():
    kw = request.args.get('kw')
    if kw:
        projects = Project.query.filter(Project.name.like('%' + kw + '%')).all()
    else:
        kw = ''
        projects = Project.query.all()

    return render_template('project_config_list.html', projects=projects, kw=kw)


@mod.route('/edit/', methods=['GET'])
@login_required
def project_config_edit():
    project_id = int(request.args.get('projectId'))
    project = Project.query.filter_by(id=project_id).one()
    return render_template('project_config_edit.html', project=project)


@mod.route('/new', methods=['GET'])
@login_required
def project_config_new_page():
    return render_template('project_config_new.html', project=None)


@mod.route('/new', methods=['POST'])
@login_required
def project_config_new():
    project_name = request.args.get('name')
    project_level = request.args.get('level')
    repo_url = request.args.get('repo_url')
    deploy_from = request.args.get('deploy_from')
    release_user = request.args.get('release_user')
    release_to = request.args.get('release_to')
    return render_template('project_config_new.html', project=None)


@mod.route('/preview/', methods=['GET'])
@login_required
def project_review():
    project_id = int(request.args.get('projectId'))
    project = Project.query.filter_by(id=project_id).one()
    return render_template('project_preview.html', project=project)


@mod.route('/group/', methods=['GET'])
@login_required
def project_group():
    project_id = int(request.args.get('projectId'))
    groups = Group.query.filter_by(project_id=project_id).all()
    project = Project.query.filter_by(id=project_id).one()
    users = User.query.filter(User.id.in_(map(lambda x: x.user_id, groups))).all()
    all_users = User.query.all()
    return render_template('project_group.html', users=users, project=project, all_users=all_users)
