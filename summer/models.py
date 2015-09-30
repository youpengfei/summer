# -*- coding: UTF-8 -*-
import hashlib
from . import db, app
from flask.ext.login import UserMixin

__author__ = 'youpengfei'


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    repo = db.Column(db.String(50))
    project_dir = db.Column(db.String(50))
    deploy_name = db.Column(db.String(50))
    description = db.Column(db.String(50))
    deploy_dir = db.Column(db.String(50))
    package_type = db.Column(db.String(50))  # mvn  gradle
    start_sh = db.Column(db.Text)
    stop_sh = db.Column(db.Text)

    def __repr__(self):
        return "<Project(name='%s', repo='%s', project_dir='%s',deploy_name='%s', description='%s',deploy_dir='%s' , start_sh='%s',stop_sh='%s')>" \
               % (self.name, self.repo, self.project_dir, self.deploy_name, self.description, self.deploy_dir,
                  self.start_sh, self.stop_sh)


class Server(db.Model):
    __tablename__ = 'server'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50))
    port = db.Column(db.Integer)
    passwd = db.Column(db.String(50))
    key_file = db.Column(db.String(50))

    def __repr__(self):
        return "<Server(ip='%s', port='%d', passwd='%s',key_file='%s')>" % (
            self.ip, self.port, self.passwd, self.key_file)


class Requirement(db.Model):
    __tablename__ = 'requirement'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    project_id = db.Column(db.Integer)
    server_list = db.Column(db.String(50))
    branch_name = db.Column(db.String(50))
    server_ip_list = []
    project_name = ''

    def __repr__(self):
        return "<Requirement(project_id='%s', server_list='%d', branch_name='%s' )>" % (
            self.project_id, self.server_list, self.branch_name)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))

    def verify_password(self, password):
        return hashlib.md5("%s-%s" % (app.config.get("PASSWORD_SALT"), password)).hexdigest() == self.password

    def __repr__(self):
        return "<User(User='%s', name='%d', email='%s',password='%s' )>" % (
            self.id, self.name, self.email, self.password)
