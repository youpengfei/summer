import subprocess

import os

from summer import app


def get_branch_list(project):
    # 应该先更新，不然在remote git删除当前选中的分支后，获取分支列表会失败
    update_repo(project)
    cmd = ['cd %s ' % get_source_path(project),
           '/usr/bin/env git pull -a',
           '/usr/bin/env git branch -r']
    command = ' && '.join(cmd)
    readlines = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.readlines()
    remote_prefix = 'origin/'
    remote_head_prefix = 'origin/HEAD'

    brand_list = []
    for readline in readlines:
        s = str(readline, encoding='utf-8')
        if s.__contains__(remote_prefix) and not s.__contains__(remote_head_prefix):
            brand_list.append(s.strip(' \n')[len(remote_prefix):])
    return brand_list


def update_repo(project, branch='master'):
    if not project.deploy_from:
        return
    git_dir = get_source_path(project)
    do_git = git_dir + '/.git'
    if os.path.exists(do_git):
        cmd = ['cd %s ' % git_dir, '/usr/bin/env git checkout -q %s' % branch, '/usr/bin/env git fetch -q --all',
               '/usr/bin/env git reset -q --hard origin/%s' % branch]
        command = ' && '.join(cmd)
        app.logger.info(command)
        popen = subprocess.Popen(command, shell=True)
        popen.wait()
    else:
        cmd = ['mkdir -p %s ' % git_dir, 'cd %s ' % git_dir, '/usr/bin/env git clone -q %s .' % project.repo_url,
               '/usr/bin/env git checkout -q %s' % branch]
        command = ' && '.join(cmd)
        app.logger.info(command)
        popen = subprocess.Popen(command, shell=True)
        popen.wait()


def update_repo_by_path(source_path, repo_url, branch='master'):
    if not source_path:
        return

    do_git = source_path + '/.git'
    if os.path.exists(do_git):
        cmd = ['cd %s ' % source_path, '/usr/bin/env git checkout -q %s' % branch, '/usr/bin/env git fetch -q --all',
               '/usr/bin/env git reset -q --hard origin/%s' % branch]
        command = ' && '.join(cmd)
        app.logger.info(command)
        popen = subprocess.Popen(command, shell=True)
        popen.wait()
    else:
        cmd = ['mkdir -p %s ' % source_path, 'cd %s ' % source_path, '/usr/bin/env git clone -q %s .' % repo_url,
               '/usr/bin/env git checkout -q %s' % branch]
        command = ' && '.join(cmd)
        app.logger.info(command)
        popen = subprocess.Popen(command, shell=True)
        popen.wait()


def get_commit_list(project, branch='master', count=20):
    # 先更新
    update_repo(project, branch)

    cmd = ['cd %s ' % (get_source_path(project)),
           '/usr/bin/env git log -%d --pretty="%%h - %%an %%s" ' % count]
    command = ' && '.join(cmd)
    readlines = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.readlines()
    commit_list = []
    for readline in readlines:
        commit_log = str(readline, encoding='utf-8').strip(' \n')
        commit_id = str(commit_log[0:commit_log.find('-') - 1])
        commit_list.append({"id": commit_id, "message": commit_log})

    return commit_list


def get_source_path(project):
    return project.deploy_from.rstrip(" /") + "/" + get_project_name(project.repo_url)


def get_project_name(repo_url):
    if not repo_url:
        return None
    else:
        return repo_url[repo_url.rfind('/') + 1:-4]


def update_to_version(task):
    project = task.project
    workspace = project.get_deploy_workspace(task.link_id)
    update_repo_by_path(source_path=workspace,
                        repo_url=project.repo_url,
                        branch=task.branch)
    cmd = ['cd %s ' % workspace, '/usr/bin/env git reset -q --hard %s' % task.commit_id]
    command = ' && '.join(cmd)
    subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    return command
