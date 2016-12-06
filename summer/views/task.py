# -*- coding: UTF-8 -*-

from flask import render_template, Blueprint
from flask import request
from flask.ext.login import current_user

import git_utils
from summer.consant import DeployEnv
from summer.models import Task, Project

__author__ = 'youpengfei'

mod = Blueprint('task', __name__)


@mod.route('/list')
def online_orders():
    user_id = current_user.id
    if request.args.get('page'):
        page = int(request.args.get('page'))
    else:
        page = 1
    count = Task.query.filter_by(user_id=user_id).count()
    tasks = Task.query.filter_by(user_id=user_id).limit(10).offset((page - 1) * 10).all()
    page_count = count / 10 if count % 10 == 0 else count / 10 + 1
    return render_template('task_list.html', tasks=tasks, page_count=page_count, page=page)


@mod.route('/new')
def add_online_order():
    projects = current_user.projects
    dev_projects = list(filter(lambda x: x.level == DeployEnv.DEV.value, projects))
    pre_release_projects = list(filter(lambda x: x.level == DeployEnv.PRE_RELEASE.value, projects))
    prod_projects = list(filter(lambda x: x.level == DeployEnv.PROD.value, projects))

    return render_template('task_new.html',
                           dev_projects=dev_projects,
                           prod_projects=prod_projects,
                           pre_release_projects=pre_release_projects)


@mod.route('/submit/<int:project_id>')
def submit_task_page(project_id):
    project = Project.query.filter_by(id=project_id).one()
    branch_list = git_utils.get_branch_list(project)
    commit_list = git_utils.get_commit_list(project)
    return render_template('task_submit.html', project=project, branch_list=branch_list, commit_list=commit_list)
