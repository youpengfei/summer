from sqlalchemy.orm import sessionmaker

__author__ = 'youpengfei'

from sqlalchemy import create_engine, Integer, Column, String, Sequence
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///summer.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
db_session = Session()


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    repo = Column(String)
    project_dir = Column(String)
    deploy_name = Column(String)
    description = Column(String)

    def __repr__(self):
        return "<Project(name='%s', repo='%s', project_dir='%s',deploy_name='%s', description='%s' )>" % (
            self.name, self.repo, self.project_dir, self.deploy_name, self.description)


class Server(Base):
    __tablename__ = 'server'
    id = Column(Integer, primary_key=True)
    ip = Column(String)
    port = Column(Integer)
    passwd = Column(String)
    key_file = Column(String)
    deploy_dir = Column(String)

    def __repr__(self):
        return "<Server(ip='%s', port='%d', passwd='%s',key_file='%s', deploy_dir='%s' )>" % (
            self.ip, self.port, self.passwd, self.key_file, self.deploy_dir)


class Requirement(Base):
    __tablename__ = 'requirement'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    server_list = Column(String)
    branch_name = Column(String)
    server_ip_list =[]
    project_name = ''

    def __repr__(self):
        return "<Requirement(project_id='%s', server_list='%d', branch_name='%s' )>" % (
            self.project_id, self.server_list, self.branch_name)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
