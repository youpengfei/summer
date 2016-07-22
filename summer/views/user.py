# -*- coding: UTF-8 -*-
import hashlib

from .. import app, db, login_manager
from ..models import User
from flask import request, redirect, render_template, jsonify, Blueprint
from flask.ext.login import login_user, login_required, current_user, logout_user

__author__ = 'youpengfei'

mod = Blueprint('user', __name__)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).one()
        if user is not None and user.verify_password(password):
            login_user(user)
            return redirect('/')

    return render_template('walle/login.html')


@mod.route('/user/list', methods=['GET', 'POST'])
def user_list():
    return render_template('walle/user_list.html')


@app.route('/password/change', methods=['GET', 'POST'])
@login_required
def password_change():
    if request.method == 'GET':
        return render_template("password_change.html")
    elif request.method == 'POST':
        password = request.form['password']
        user = User.query.get(current_user.id)
        user.password = hashlib.md5(
            str("%s-%s" % (app.config.get("PASSWORD_SALT"), password)).encode('utf-8')).hexdigest()
        db.session.add(user)
        db.session.commit()
        return jsonify(code=200, message="修改成功")


@app.route('/registers', methods=['GET', 'POST'])
def user_register():
    if request.method == 'GET':
        return render_template("walle/register.html")
    elif request.method == 'POST':
        password = request.form['password']
        user = User.query.get(current_user.id)
        user.password = hashlib.md5(
            str("%s-%s" % (app.config.get("PASSWORD_SALT"), password)).encode('utf-8')).hexdigest()
        db.session.add(user)
        db.session.commit()
        return jsonify(code=200, message="修改成功")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@login_manager.user_loader
def get_user(ident):
    return User.query.get(int(ident))
