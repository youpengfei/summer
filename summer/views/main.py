# -*- coding: UTF-8 -*-
from flask import Blueprint
from flask import redirect
from flask import url_for
from flask_login import login_required

mod = Blueprint('main', __name__)


@mod.route('/')
@login_required
def index():
    return redirect(url_for('task.online_orders'))
