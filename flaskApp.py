"""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
#!/usr/bin/env python3

from flask import Flask, redirect, url_for, render_template, request, flash, jsonify, abort
from models import db, Contact

# Importing custom application configurations
from config import *

# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my secret'
app.config['DEBUG'] = False

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+SQLITE_DB_NAME
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/book'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
import requests

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route("/new_contact", methods=('GET', 'POST'))
def new_contact():
    '''
    Create new contact
    '''
    #check to see that all required fields are present, otherwise throw exception
    neededKeys=('id','first','last','email','officephone','mobilephone')
    if all(key in request.json for key in neededKeys):
        my_contact = Contact(id=request.json["id"],
                         first=request.json["first"],
                         last=request.json["last"],
                         email=request.json["email"],
                         officephone=request.json["officephone"],
                         mobilephone=request.json["mobilephone"]
                         )
        db.session.add(my_contact)
        try:
            db.session.commit()
            # User info
            resp = jsonify(my_contact.dict())
            if resp != {}:
                resp.status_code = 200
                return resp
            else:
                return not_found()
        except:
            db.session.rollback()
            return not_found()
    else:
        abort(400)



@app.route("/contacts")
def contacts():
    '''
    Show alls contacts
    '''
    contacts = Contact.query.order_by(Contact.last).all()
    print(contacts)
    theContactsList=[]
    for contact in contacts:
        theContactsList.append(contact.dict())
    resp = jsonify(theContactsList)
    if resp!={}:
        resp.status_code = 200
        return resp
    else:
        return not_found()


@app.route("/search")
def search():
    '''
    Search
    '''
    if not request.json:
        abort(400)

    first_search = last_search = email_search = ''
    if 'first' in request.json:
        first_search = request.json['first']
    if 'last' in request.json:
        last_search = request.json['last']
    if 'email' in request.json:
        email_search = request.json['email']
    all_contacts = Contact.query.filter(
            Contact.email.contains(email_search),Contact.first.contains(first_search),Contact.last.contains(last_search)
            ).order_by(Contact.last).all()

    theContactsList = []
    for contact in all_contacts:
        theContactsList.append(contact.dict())
    resp = jsonify(theContactsList)

    if resp!={}:
        resp.status_code = 200
        return resp
    else:
        return not_found()

@app.route("/searchall",methods=('GET', 'POST'))
def searchall():
    '''
    Search
    '''
    if not request.json:
        print("No data in request..")
        abort(400)

    print(request.json)
    full_search=""
    if 'search_string' in request.json:
        full_search=request.json['search_string']

    all_contacts = Contact.query.filter(
            Contact.last.contains(full_search)
            ).order_by(Contact.last).all()
    if not all_contacts:
        all_contacts = Contact.query.filter(
            Contact.first.contains(full_search)
            ).order_by(Contact.last).all()
    if not all_contacts:
        all_contacts = Contact.query.filter(
            Contact.email.contains(full_search)
            ).order_by(Contact.last).all()


    theContactsList = []
    for contact in all_contacts:
        theContactsList.append(contact.dict())
    resp = jsonify(theContactsList)

    if resp!={}:
        resp.status_code = 200
        return resp
    else:
        return not_found()

@app.route("/contacts/delete", methods=('POST',))
def contacts_delete():
    '''
    Delete contact
    '''
    try:
        mi_contacto = Contact.query.filter_by(id=request.json['id']).first()
        print(mi_contacto)
        db.session.delete(mi_contacto)
        db.session.commit()
    except:
        db.session.rollback()
        message = {
            'status': 500,
            'message': 'Internal error:',
        }
        resp = jsonify(message)
        resp.status_code = 500
        return resp

    message = {
            'status': 200,
            'message': 'Successfully deleted.',
        }
    resp = jsonify(message)
    resp.status_code = 200
    return resp

if __name__ == "__main__":
    
    app.jinja_env.cache = {}
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)