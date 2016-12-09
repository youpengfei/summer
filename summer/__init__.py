from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.socketio import SocketIO
from flask.ext.sqlalchemy import SQLAlchemy



__author__ = 'youpengfei'

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

socketio = SocketIO(app)

from .views import requirement, project, server, main, user,task,project_config


# app.register_blueprint(requirement.mod, url_prefix='/requirement')
app.register_blueprint(project.mod, url_prefix='/project')
app.register_blueprint(project_config.mod, url_prefix='/project/config')
# app.register_blueprint(server.mod, url_prefix='/server')
app.register_blueprint(task.mod, url_prefix='/task')
app.register_blueprint(main.mod)
app.register_blueprint(user.mod)

