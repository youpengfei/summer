# -*- coding: UTF-8 -*-

from flask import redirect, jsonify
from flask import render_template, Blueprint
from flask import request
from flask import url_for
from flask.ext.login import current_user, login_required

import git_utils
from summer import db
from summer import deploy
from summer.consant import DeployEnv
from summer.models import Task, Project, Record

__author__ = 'youpengfei'

mod = Blueprint('task', __name__)


@mod.route('/list')
@login_required
def online_orders():
    user_id = current_user.id
    if request.args.get('page'):
        page = int(request.args.get('page'))
    else:
        page = 1
    count = Task.query.filter_by(user_id=user_id).count()
    tasks = Task.query.filter_by(user_id=user_id) \
        .order_by(Task.updated_at.desc()) \
        .limit(10).offset((page - 1) * 10).all()
    page_count = count / 10 if count % 10 == 0 else count / 10 + 1
    return render_template('task_list.html', tasks=tasks, page_count=page_count, page=page)


@mod.route('/new', methods=['GET'])
@login_required
def add_online_order_page():
    projects = current_user.projects
    dev_projects = list(filter(lambda x: x.level == DeployEnv.DEV.value, projects))
    pre_release_projects = list(filter(lambda x: x.level == DeployEnv.PRERELEASE.value, projects))
    prod_projects = list(filter(lambda x: x.level == DeployEnv.PROD.value, projects))

    return render_template('task_new.html',
                           dev_projects=dev_projects,
                           prod_projects=prod_projects,
                           pre_release_projects=pre_release_projects)


@mod.route('/delete', methods=['GET'])
@login_required
def delete_task():
    task_id = int(request.args.get('taskId'))
    one = Task.query.filter_by(id=task_id).one()
    db.session.delete(one)
    db.session.commit()
    return jsonify(code=200)


@mod.route('/submit/<int:project_id>', methods=['GET'])
@login_required
def submit_task_page(project_id):
    project = Project.query.filter_by(id=project_id).one()
    branch_list = git_utils.get_branch_list(project)
    return render_template('task_submit.html', project=project, branch_list=branch_list)


@mod.route('/submit', methods=['POST'])
@login_required
def add_online_order():
    title = request.form.get('title', None)
    branch = request.form.get('branch')
    file_transmission_mode = request.form.get('fileTransmissionMode')
    commit_id = request.form.get('commitId')
    project_id = int(request.args.get('projectId'))

    project = Project.query.filter_by(id=project_id).one()

    task = Task()
    task.project_id = project_id
    task.title = title
    task.branch = branch
    task.commit_id = commit_id
    task.user_id = current_user.id
    if project.audit == 0:
        task.status = 1
    else:
        task.status = 0
    task.link_id = ''
    task.file_transmission_mode = file_transmission_mode if file_transmission_mode else '1'
    db.session.add(task)
    db.session.commit()

    return redirect(url_for('task.online_orders'))


@mod.route('/deploy', methods=['GET'])
@login_required
def deploy_index():
    task_id = int(request.args.get('taskId'))
    task = Task.query.filter_by(id=task_id).one()
    return render_template('task_deploy.html', task=task)


@mod.route('/deploy', methods=['POST'])
@login_required
def deploy_start():
    task_id = int(request.form.get('taskId'))
    return deploy.start_deploy(task_id)


@mod.route('/get-process', methods=['GET'])
@login_required
def task_process():
    task_id = int(request.args.get('taskId'))
    if Record.query.filter_by(task_id=task_id).count() > 0:
        one = Record.query.filter_by(task_id=task_id).order_by(Record.action.desc()).limit(1).one()
    else:
        one = {}
    return jsonify(data={"code": 200, "percent": one.action})


@mod.route('/rollback', methods=['GET'])
@login_required
def rollback_task():
    task_id = int(request.args.get('taskId'))
    task = Task.query.filter_by(id=task_id).one()
    if not task:
        return jsonify(code=404, message="任务不存在")

    if task.user_id != current_user.id:
        return jsonify(code=403, message="这个不是你的任务")

    if task.link_id == task.ex_link_id:
        return jsonify(code=500, message="不可以回滚两次")

    project = task.project
    status = 1 if project.audit == 0 else 0
    rollback_task_model = Task()
    rollback_task_model.status = status
    rollback_task_model.action = 1
    rollback_task_model.link_id = task.ex_link_id
    rollback_task_model.title = task.title + '-回滚'
    rollback_task_model.user_id = current_user.id
    rollback_task_model.project_id = task.project.id
    rollback_task_model.file_transmission_mode = task.file_transmission_mode
    rollback_task_model.commit_id = task.commit_id
    rollback_task_model.branch = task.branch
    db.session.add(rollback_task_model)
    db.session.commit()
    url = '/task/' if project.audit == 1 else '/task/deploy?taskId=%d' % rollback_task_model.id
    return jsonify(data={"url": url})
