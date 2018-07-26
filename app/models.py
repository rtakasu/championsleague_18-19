from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import pickle

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	bracket = db.Column(db.PickleType)
	points = db.Column(db.Integer)
	valid = db.Column(db.Boolean, default=False) # Post is only valid if it's the latest submission for a user

	def __repr__(self):
		return '<Post {}>'.format(self.get_bracket())

	# User pickle dumps to save serialized dict into bracket column
	def set_bracket(self, bracket_dict):
		self.bracket = pickle.dumps(bracket_dict)

	# Unpickle and return bracket dict
	def get_bracket(self):
		return pickle.loads(self.bracket)

	def make_valid(self):
		posts = Post.query.filter(id!=self.id).all()
		for post in posts:
			post.valid = False
		self.valid = True

class Tournament(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	games = db.Column(db.PickleType)

	def __init__(self):
		self.games = pickle.dumps({'winner':None})

	def set_games(self, games_dict):
		self.games = pickle.dumps(games_dict)

	def get_games(self):
		return pickle.loads(self.games)

	def calculate_points(self):
		posts = Post.query.all()
		for post in posts:
			post.points = self.calculate_points_specific(post)

	def calculate_points_specific(self, post):
		if post.get_bracket()['winner'] == self.get_games()['winner']:
			return 3
		else:
			return 0 

	
@login.user_loader
def load_user(id):
	return User.query.get(int(id))


