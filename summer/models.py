# -*- coding: UTF-8 -*-
import bcrypt
from flask.ext.login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from . import db

__author__ = 'youpengfei'


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer)
    level = db.Column(db.Integer)
    status = db.Column(db.Integer)
    version = db.Column(db.String(32))
    repo_url = db.Column(db.String(200))
    repo_username = db.Column(db.String(50))
    repo_password = db.Column(db.String(100))
    repo_mode = db.Column(db.String(50))
    repo_type = db.Column(db.String(10))
    deploy_from = db.Column(db.String(200))
    excludes = db.Column(db.Text)
    release_user = db.Column(db.String(50))
    release_to = db.Column(db.String(200))
    release_library = db.Column(db.String(200))
    hosts = db.Column(db.Text)
    pre_deploy = db.Column(db.Text)
    post_deploy = db.Column(db.Text)
    pre_release = db.Column(db.Text)
    post_release = db.Column(db.Text)
    post_release_delay = db.Column(db.Integer)
    audit = db.Column(db.Integer)
    ansible = db.Column(db.Integer)
    keep_version_num = db.Column(db.Integer)
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)
    tasks = relationship("Task", back_populates="project")

    def __repr__(self, *args, **kwargs):
        return super().__repr__(*args, **kwargs)


projects = db.Table('group',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('project_id', db.Integer, db.ForeignKey('project.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    is_email_verified = db.Column(db.Integer)
    auth_key = db.Column(db.String(32))
    password_hash = db.Column(db.String(255))
    email_confirmation_token = db.Column(db.String(255))
    email = db.Column(db.String(255))
    avatar = db.Column(db.String(100))
    role = db.Column(db.Integer)
    status = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    realname = db.Column(db.String(32))
    tasks = relationship("Task", back_populates="user")
    projects = db.relationship('Project', secondary=projects,
                               backref=db.backref('users', lazy='dynamic'))

    def verify_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), self.password_hash.encode('utf-8')) == self.password_hash.encode(
            'utf-8')


class Group(db.Model):
    __tablename__ = 'group'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer,db.ForeignKey('project.id'))
    type = db.Column(db.Integer)


class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    project_id = db.Column(db.Integer, ForeignKey('project.id'))
    action = db.Column(db.Integer)
    status = db.Column(db.SmallInteger)
    title = db.Column(db.String(100))
    link_id = db.Column(db.String(20))
    ex_link_id = db.Column(db.String(20))
    commit_id = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    file_transmission_mode = db.Column(db.SmallInteger)
    file_list = db.Column(db.Text)
    enable_rollback = db.Column(db.SmallInteger)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    user = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")


class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)
    status = db.Column(db.SmallInteger)
    action = db.Column(db.SmallInteger)
    command = db.Column(db.Text)
    duration = db.Column(db.Integer)
    memo = db.Column(db.Text)
    created_at = db.Column(db.Integer)


class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    expire = db.Column(db.Integer)
    data = db.Column(db.BLOB)
