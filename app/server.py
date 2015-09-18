# -*- coding: UTF-8 -*-

from app import app, db
from app.models import Server
from flask import request, render_template, redirect
from ssh_help import command_with_result

__author__ = 'youpengfei'


@app.route("/server/add", methods=['POST', 'GET'])
def server_add():
    if request.method == 'GET':
        return render_template("server_add.html", active="server")
    elif request.method == 'POST':
        ip = request.form['ip']
        port = request.form['port']
        passwd = request.form['passwd']
        key_file = request.form['key_file']
        server = Server(ip=ip, port=port, passwd=passwd, key_file=key_file)
        db.session.add(server)
        db.session.commit()
        return redirect('/server/list')


@app.route("/server/list", methods=['POST', 'GET'])
def server_list():
    servers = Server.query.all()
    return render_template('server_list.html', server_list=servers, active="server")


@app.route("/server/log/<int:server_id>")
def logs(server_id):
    server = Server.query.filter_by(id=server_id).one()
    result = command_with_result(server.ip, server.key_file,
                                 'tail -n200 %s/%s ' % (server.deploy_dir, 'logs/gpc-j.log'))
    print result
    return render_template('project_log.html', result=result)
