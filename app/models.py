from app import db

__author__ = 'youpengfei'


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    repo = db.Column(db.String)
    project_dir = db.Column(db.String)
    deploy_name = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return "<Project(name='%s', repo='%s', project_dir='%s',deploy_name='%s', description='%s' )>" % (
            self.name, self.repo, self.project_dir, self.deploy_name, self.description)


class Server(db.Model):
    __tablename__ = 'server'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String)
    port = db.Column(db.Integer)
    passwd = db.Column(db.String)
    key_file = db.Column(db.String)
    deploy_dir = db.Column(db.String)

    def __repr__(self):
        return "<Server(ip='%s', port='%d', passwd='%s',key_file='%s', deploy_dir='%s' )>" % (
            self.ip, self.port, self.passwd, self.key_file, self.deploy_dir)


class Requirement(db.Model):
    __tablename__ = 'requirement'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer)
    server_list = db.Column(db.String)
    branch_name = db.Column(db.String)
    server_ip_list = []
    project_name = ''

    def __repr__(self):
        return "<Requirement(project_id='%s', server_list='%d', branch_name='%s' )>" % (
            self.project_id, self.server_list, self.branch_name)


if __name__ == '__main__':
    db.create_all()
