#!summer/bin/python
import sys
from app import app, db

if __name__ == '__main__':
    sys.setdefaultencoding('utf-8')
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
