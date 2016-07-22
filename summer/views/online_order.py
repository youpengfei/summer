# -*- coding: UTF-8 -*-

from flask import request, render_template, redirect, jsonify, Blueprint

__author__ = 'youpengfei'

mod = Blueprint('online_order', __name__)


@mod.route('/list')
def online_orders():
    return render_template('walle/online_list.html')


@mod.route('/new')
def add_online_order():
    return render_template('walle/online_order_new.html')
