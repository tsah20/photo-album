#!/usr/bin/env python
import os
from flask import Flask, abort, request, jsonify, g, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import json

# initialization
app = Flask(__name__)
api = Api(app)
ma = Marshmallow(app)
app.config['SECRET_KEY'] = 'we can set it anything we want'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
CORS(app)

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)


    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

class Photo(db.Model):
    __tablename__='photos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    date = db.Column(db.String(120), unique=False)
    location = db.Column(db.String(120), unique=False)
    url = db.Column(db.String(120), unique=True)

    def __init__(self, name, date, location, url):
        self.name = name
        self.date = date
        self.location = location
        self.url = url

class PhotoSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("name", "date", "location", "url")

photo_schema = PhotoSchema()
photos_schema = PhotoSchema(many=True)
base_url = 'http://localhost:5000'


@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('images', path)


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.query.filter_by(username=username_or_token).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@app.route('/api/register', methods=['POST'])
def new_user():
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username, first_name=first_name, last_name=last_name)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user is None or not pwd_context.verify(password, user.password_hash):
        result = json.dumps({"error":"Invalid username and password"})
    else:
        result = json.dumps({'password':password, 'username': username, 'first_name': user.first_name, 'last_name':user.last_name})
    print(result)
    return result

@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


# Photo resource [just a helper function]
@app.route('/api/photos', methods=['POST'])
@auth.login_required
def post_photos():
    # put the list of photos from the database.
    name = request.json['name']
    date = request.json['date']
    location = request.json['location']
    url = '{}/images/{}'.format(base_url, name)
    photo_obj = Photo(name, date, location, url)
    db.session.add(photo_obj)
    db.session.commit()
    return (jsonify({'name': name, 'date': date, 'location':location, 'url': url}), 201,
            {'Location': url_for('get_user', id=g.user.id, _external=True)})

@app.route('/api/allphotos')
def get_all_photos():
    # get the list of photos from the database.
    all_photos = Photo.query.all()
    return photos_schema.jsonify(all_photos)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)