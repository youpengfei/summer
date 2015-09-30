# -*- coding: UTF-8 -*-

from ..models import Server, db
from flask import request, render_template, redirect, Blueprint

__author__ = 'youpengfei'

mod = Blueprint('server', __name__)


@mod.route("/add", methods=['POST', 'GET'])
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


@mod.route("/list", methods=['POST', 'GET'])
def server_list():
    servers = Server.query.all()
    return render_template('server_list.html', server_list=servers, active="server")


@mod.route("/delete/<int:server_id>")
def delete(server_id):
    server = Server.query.filter_by(id=server_id).one()
    db.session.delete(server)
    db.session.commit()
    return redirect('/server/list')
