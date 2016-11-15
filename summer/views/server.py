# # -*- coding: UTF-8 -*-
# from flask_login import login_required
#
# from ..models import Server, db, Requirement
# from flask import request, render_template, redirect, Blueprint, jsonify
#
# __author__ = 'youpengfei'
#
# mod = Blueprint('server', __name__)
#
#
# @mod.route("/add", methods=['POST', 'GET'])
# @login_required
# def server_add():
#     if request.method == 'GET':
#         return render_template("server_add.html", active="server")
#     elif request.method == 'POST':
#         ip = request.form['ip']
#         port = request.form['port']
#         passwd = request.form['passwd']
#         key_file = request.form['key_file']
#         server = Server(ip=ip, port=port, passwd=passwd, key_file=key_file)
#         db.session.add(server)
#         db.session.commit()
#         return redirect('/server/list')
#
#
# @mod.route("/list", methods=['POST', 'GET'])
# @login_required
# def server_list():
#     servers = Server.query.all()
#     return render_template('server_list.html', server_list=servers, active="server")
#
#
# @mod.route("/id_list/<int:requirement_id>", methods=['POST', 'GET'])
# @login_required
# def server_id_list(requirement_id):
#     requirement = Requirement.query.filter_by(id=requirement_id).one()
#     servers = Server.query.filter(Server.id.in_(requirement.server_list.split(","))).all()
#     return jsonify(code=200, server_id_list=[x.ip for x in servers])
#
#
# @mod.route("/delete/<int:server_id>")
# @login_required
# def delete(server_id):
#     server = Server.query.filter_by(id=server_id).one()
#     db.session.delete(server)
#     db.session.commit()
#     return redirect('/server/list')
