# -*- coding: UTF-8 -*-
import hashlib
from flask import request, redirect, render_template, jsonify, Blueprint
from flask.ext.login import login_user, login_required, current_user, logout_user

from .. import app, db, login_manager
from ..models import User

__author__ = 'youpengfei'

mod = Blueprint('user', __name__)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remeber_me = request.form.get('remember_me', False)
        user = User.query.filter_by(email=email).one()
        if user is not None and user.verify_password(password):
            login_user(user, remember=remeber_me)
            return redirect('/')
        else:
            return render_template('login.html', error_message='用户名或者密码错误')
    else:
        return render_template('login.html')


@mod.route('/user/list', methods=['GET', 'POST'])
def user_list():
    users = User.query.all()
    return render_template('user_list.html', users=users)


@mod.route('/user/add', methods=['GET'])
def user_add():
    return render_template('user_add.html')


@mod.route('/user/add', methods=['POST'])
def add_user():
    return render_template('user_list.html')


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
        return render_template("register.html")
    elif request.method == 'POST':
        password = request.form['password']
        user = User.query.get(current_user.id)
        user.password = hashlib.md5(
            str("%s-%s" % (app.config.get("PASSWORD_SALT"), password)).encode('utf-8')).hexdigest()
        db.session.add(user)
        db.session.commit()
        return jsonify(code=200, message="修改成功")


@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    user = User.query.filter_by(id=user_id).one()
    return render_template("user_profile.html", user_info=user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@login_manager.user_loader
def get_user(ident):
    return User.query.get(int(ident))


@app.route('/user/reset-password', methods=['GET'])
@login_required
def reset_password_page():
    return render_template("reset-password.html")


@app.route('/user/reset-password', methods=['POST'])
@login_required
def reset_password():
    new_password = request.args.get('newPassword')
    return render_template("reset-password.html")
