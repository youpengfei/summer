# -*- coding: UTF-8 -*-

from flask import Blueprint, jsonify
from flask import request
from flask_login import login_required

import git_utils
from summer.models import Project

__author__ = 'youpengfei'

mod = Blueprint('project', __name__)


@mod.route('/get-branch', methods=['GET'])
@login_required
def get_branch():
    project_id = int(request.args.get('projectId'))
    project = Project.query.filter_by(id=project_id).one()
    branch_list = git_utils.get_branch_list(project)
    return jsonify(data=branch_list, code=200)


@mod.route('/get-commit-history', methods=['GET'])
@login_required
def get_commit_list():
    project_id = int(request.args.get('projectId'))
    branch = request.args.get('branch')
    project = Project.query.filter_by(id=project_id).one()
    commit_list = git_utils.get_commit_list(project, branch=branch, count=10)
    return jsonify(data=commit_list, code=200)
