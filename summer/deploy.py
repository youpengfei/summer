import datetime
import subprocess
import time

from flask import jsonify
from flask.ext.login import current_user

import git_utils
import utils
from summer import db, app
from summer.models import Task, Record


def start_deploy(task_id):
    if not task_id:
        return jsonify(code=401, message='taskId必须填写')

    task = Task.query.filter_by(id=task_id).one()

    if task.user_id != current_user.id:
        return jsonify(code=403, message="这个任务不属于你")

    # 任务失败或者审核通过时可发起上线
    if not (1, 4).__contains__(task.status):
        return jsonify(code=500, message="任务不是失败或者审核通过状态")

    # 清除历史记录
    Record.query.filter_by(task_id=task_id).delete()

    if task.action == 0:
        make_version(task)
        init_workspace(task)
        pre_deploy(task)
        revision_update(task)
        post_deploy(task)
        transmission(task)
        update_remote_server(task)
        clean_remote_server(task)
        clean_local(task)
        task.status = 3
        task.ex_link_id = task.project.version
        project = task.project
        project.version = task.link_id
        db.session.add(project)
        db.session.add(task)
    else:
        update_remote_server(task)
        task.status = 3
        task.ex_link_id = task.project.version
        project = task.project
        project.version = task.link_id
        db.session.add(project)
        db.session.add(task)

    db.session.commit()
    jsonify(message="成功", code=0)


def make_version(task):
    version = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    task.link_id = version
    db.session.add(task)


def init_workspace(task):
    from_time = int(1000 * time.time())
    project = task.project
    project_name = git_utils.get_project_name(project.repo_url)
    build_path = "%s/%s-%s-%s" % (project.deploy_from, project_name, project.level, task.link_id)
    # 拷贝本地文件
    subprocess.Popen('cp -rf  %s %s' % (git_utils.get_source_path(project), build_path), shell=True)
    # 拷贝远程文件
    for host in project.hosts.split('\n'):
        version = '%s/%s/%s' % (project.release_library, project_name, task.link_id)
        utils.command_with_result(hostname=host, command='mkdir -p %s' % version)

    record = Record(user_id=current_user.id, task_id=task.id, action=24, duration=int(1000 * time.time()) - from_time)
    db.session.add(record)
    return


def pre_deploy(task):
    project = task.project
    from_time = int(1000 * time.time())
    pre_deploy_split = task.project.pre_deploy.split('\n')
    if pre_deploy_split is None:
        return

    cmd = ['. /etc/profile', 'cd %s' % project.get_deploy_workspace(task.link_id)]

    for pre_deploy_cmd in pre_deploy_split:
        if pre_deploy_cmd:
            cmd.append(pre_deploy_cmd)

    subprocess.Popen(' && '.join(cmd), shell=True, stdout=subprocess.PIPE)

    record = Record(user_id=current_user.id,
                    task_id=task.id,
                    action=40,
                    duration=int(1000 * time.time()) - from_time,
                    command=' && '.join(cmd))
    db.session.add(record)
    db.session.commit()
    return


def revision_update(task):
    from_time = int(1000 * time.time())
    cmd = git_utils.update_to_version(task)
    record = Record(user_id=current_user.id,
                    task_id=task.id,
                    action=53,
                    duration=int(1000 * time.time()) - from_time,
                    command=cmd)
    db.session.add(record)
    db.session.commit()
    return


def post_deploy(task):
    from_time = int(1000 * time.time())
    project = task.project
    tasks = project.post_deploy.split('\n')

    # 本地可能要做一些依赖环境变量的命令操作
    cmd = ['. /etc/profile']
    workspace = project.get_deploy_workspace(task.link_id)

    # 简化用户切换目录，直接切换到当前部署空间：{deploy_from}/{env}/{project}-YYmmdd-HHiiss
    cmd.append("cd %s" % workspace)

    for task_command in tasks:
        if task_command:
            cmd.append(task_command.strip('\r\n'))

    command = ' && '.join(cmd)
    popen = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    popen.wait()
    if popen.stderr:
        app.logger.error(popen.stderr.readlines())

    app.logger.info(popen.stdout.readlines())
    db.session.commit()

    record = Record(user_id=current_user.id,
                    task_id=task.id,
                    action=64,
                    duration=int(1000 * time.time()) - from_time,
                    command=command)
    db.session.add(record)
    return


def transmission(task):
    from_time = int(1000 * time.time())
    project = task.project
    package_file_full_name = package_file(task)
    remote_file_name = get_release_file(project, task)

    for host in project.hosts.split('\n'):
        utils.trans_data(hostname=host, remote_path=remote_file_name, local_path=package_file_full_name)

    un_package_file(task)

    record = Record(user_id=current_user.id,
                    task_id=task.id,
                    action=78,
                    duration=int(1000 * time.time()) - from_time,
                    command='scp ')
    db.session.add(record)
    db.session.commit()


def update_remote_server(task):
    project = task.project
    cmd = [get_remote_command(project.pre_release, task.link_id, project),
           get_linked_command(task),
           get_remote_command(project.post_release, task.link_id, project)]
    from_time = int(1000 * time.time())
    command = ' && '.join(cmd)
    for host in project.hosts.split('\n'):
        utils.command_with_result(hostname=host, command=command)

    record = Record(user_id=current_user.id,
                    task_id=task.id,
                    action=100,
                    duration=int(1000 * time.time()) - from_time,
                    command=command)

    db.session.add(record)
    db.session.commit()


def clean_remote_server(task):
    project = task.project
    cmd = ['cd %s/%s/%s' % (project.release_library, git_utils.get_project_name(project.repo_url), task.link_id),
           'rm -f %s/%s/*.tar.gz' % (
               project.release_library, git_utils.get_project_name(project.repo_url)),
           'ls -1 | sort -r | awk \'FNR > %d  {printf("rm -rf %%s\n", $0);}\' | bash' % project.keep_version_num
           ]

    for host in project.hosts.split('\n'):
        utils.command_with_result(hostname=host, command=' && '.join(cmd))


def clean_local(task):
    project = task.project
    subprocess.Popen('rm -rf %s*' % project.get_deploy_workspace(task.link_id), shell=True)
    return


def get_release_file(project, task):
    return '%s/%s/%s.tar.gz' % (project.release_library, git_utils.get_project_name(project.repo_url), task.link_id)


def get_excludes(excludes):
    excludes_cmd = ''

    # 无论是否填写排除.git和.svn, 这两个目录都不会发布
    excludes.append('.git')
    excludes.append('.svn')

    for exclude in excludes:
        excludes_cmd += "--exclude=%s" % exclude.strip(' ')

    return excludes_cmd


def package_file(task):
    project = task.project
    version = task.link_id
    files = task.get_deploy_files()
    excludes = project.excludes.split('\n ')
    package_path = '%s.tar.gz' % project.get_deploy_workspace(version)
    package_command = 'cd %s/ && tar -p %s -cz -f %s %s' % \
                      (project.get_deploy_workspace(version), get_excludes(excludes), package_path, files)

    subprocess.Popen(package_command, shell=True, stdout=subprocess.PIPE)
    return package_path


def un_package_file(task):
    project = task.project
    version = task.link_id
    release_file = get_release_file(project, task)
    web_root_path = project.release_to
    release_path = '%s/%s/%s' % (project.release_library, git_utils.get_project_name(project.repo_url), version)
    cmd = []
    if task.file_transmission_mode == 2:
        cmd.append('cp -arf %s/. %s' % web_root_path % release_path)

    cmd.append(
        'cd %s$s && tar --no-same-owner -pm -C %s$s -xz -f %s$s' % (release_path, release_path, release_file))
    command = ' && '.join(cmd)
    for host in project.hosts.split('\n'):
        utils.command_with_result(hostname=host, command=command)


def get_remote_command(task, version, project):
    task_split = task.split('\n')
    cmd = ['. /etc/profile']
    version1 = '%s/%s/%s' % (project.release_library, git_utils.get_project_name(project.repo_url), version)

    cmd.append('cd %s' % version1)

    for task in task_split:
        cmd.append(task.strip('\r\n'))

    return ' && '.join(cmd)


def get_linked_command(task):
    project = task.project
    release_user = project.release_user
    project_name = git_utils.get_project_name(project.repo_url)
    current_tmp = '%s/%s/current-%s.tmp' % (project.release_library, project_name, project_name)
    linked_from = '%s/%s/%s' % (project.release_library, project_name, task.link_id)
    cmd = ['ln -sfn %s %s' % (linked_from, current_tmp),
           'chown -h %s %s' % (release_user, current_tmp),
           'mv -fT %s %s' % (current_tmp, project.release_to)]
    return ' && '.join(cmd)
