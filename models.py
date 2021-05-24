from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
from config import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + SQLITE_DB_NAME
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Contact(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.Integer,db.Sequence('Contact_seq_id'),primary_key=True)
    first = db.Column(db.String(80), nullable=False,unique=True)
    last = db.Column(db.String(100), nullable=True)
    isdnnumber = db.Column(db.String(100), nullable=True)
    isdnnumbertwo = db.Column(db.String(100), nullable=True)
    isdnbandwidth = db.Column(db.String(100),nullable=True)
    restricted = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(200), nullable=True, unique=True)
    h23 = db.Column(db.String(100), nullable=True)
    ipaddress = db.Column(db.String(100), nullable=True)
    ipbandwidth = db.Column(db.String(100), nullable=True)
    externalid = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        theDict={
            "id": self.id,
            "first": self.first,
            "last": self.last,
            "isdnnumber": self.isdnnumber,
            "isdnnumbertwo": self.isdnnumbertwo,
            "isdnbandwidth": self.isdnbandwidth,
            "restricted": self.restricted,
            "phone" : self.phone,
            "email": self.email,
            "h23":  self.h23,
            "ipaddress" : self.ipaddress,
            "ipbandwidth": self.ipbandwidth,
            "externalid" : self.externalid
        }
        return json.dumps(theDict)

    def dict(self):
        theDict={
            "id": self.id,
            "first": self.first,
            "last": self.last,
            "isdnnumber": self.isdnnumber,
            "isdnnumbertwo": self.isdnnumbertwo,
            "isdnbandwidth": self.isdnbandwidth,
            "restricted": self.restricted,
            "phone" : self.phone,
            "email": self.email,
            "h23":  self.h23,
            "ipaddress" : self.ipaddress,
            "ipbandwidth": self.ipbandwidth,
            "externalid" : self.externalid
        }
        return theDict