from app import app

# ------

# from flask import Flask, flash, redirect, render_template, request, session, abort, url_for

# from flask_login import LoginManager, UserMixin, login_required, current_user, login_user
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# import os

# basedir = os.path.abspath(os.path.dirname(__file__))

# class Config(object):
# 	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
# 	SQLALCHEMY_TRACK_MODIFICATIONS = False

# app = Flask(__name__)
# db = SQLAlchemy()
# app.config.from_object(Config)


# login = LoginManager(app)
# @login.user_loader
# def load_user(id):
#     return User.query.get(int(id))
# login.init_app(app)


# class User(UserMixin, db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	username = db.Column(db.String(64), index=True, unique=True)
# 	email = db.Column(db.String(120), index=True, unique=True)
# 	password_hash = db.Column(db.String(128))

# 	def __repr__(self):
# 		return '<User {}>'.format(self.username)  

# 	def set_password(self, password):
# 		self.password_hash = generate_password_hash(password)

# 	def check_password(self, password):
# 		return check_password_hash(self.password_hash, password)




