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
	group_stage_guess = db.Column(db.PickleType)
	R16_guess = db.Column(db.PickleType)
	QF_guess = db.Column(db.PickleType)
	SF_guess = db.Column(db.PickleType)
	F_guess = db.Column(db.PickleType)

	def __repr__(self):
		return '<Post {}>'.format(self.get_bracket())

	# User pickle dumps to save serialized dict into bracket column
	# TO DELETE
	def set_bracket(self, bracket_dict):
		self.bracket = pickle.dumps(bracket_dict)

	# Unpickle and return bracket dict
	# TO DELETE
	def get_bracket(self):
		if self.bracket:
			return pickle.loads(self.bracket)
		return None

	def set_group_guess(self, group_stage_guess):
		self.group_stage_guess = pickle.dumps(group_stage_guess)

	def get_group_guess(self):
		if self.group_stage_guess:
			return pickle.loads(self.group_stage_guess)
		return None

	def make_valid(self):
		posts = Post.query.filter(id!=self.id).all()
		for post in posts:
			post.valid = False
		self.valid = True

class Tournament(db.Model):
	id = db.Column(db.Integer, primary_key=True)

	# X_games contains a dict with the info about each real-world game
	# X_teams contains a dict with the teams in that round and their corresponding key
	games = db.Column(db.PickleType)
	group_stage_games = db.Column(db.PickleType)
	group_stage_teams = db.Column(db.PickleType)
	R16_games = db.Column(db.PickleType)
	R16_teams = db.Column(db.PickleType)
	QF_games = db.Column(db.PickleType)
	QF_teams = db.Column(db.PickleType)
	SF_games = db.Column(db.PickleType)
	SF_teams = db.Column(db.PickleType)
	F_game = db.Column(db.PickleType)
	F_teams = db.Column(db.PickleType)

	def __init__(self):
		self.group_stage_games = pickle.dumps(helper_group_stage())

	def set_group_stage(self, group_stage_games):
		self.group_stage_games = pickle.dumps(group_stage_games)

	def get_group_stage(self):
		if self.group_stage_games:
			return pickle.loads(self.group_stage_games)
		return None

	def calculate_points(self):
		posts = Post.query.all()
		for post in posts:
			post.points = self.calculate_points_specific(post)

	def calculate_points_specific(self, post):
		return 1

	def get_R16_teams(self):
		if self.R16_teams:
			return pickle.loads(self.R16_teams)
		return None

	def set_R16_teams(self, teams):
		self.R16_teams = pickle.dumps(teams)

	def helper_group_stage():
		games_dict = {}
		groups = ("A", "B", "C", "D", "E", "F", "G", "H")
		for group_letter in groups:
			for home_team in range(1,5):
				for away_team in range(1,5):
					if home_team != away_team:
						key = group_letter + str(home_team) + "H" + "vs" + group_letter + str(away_team) + "A"
						games_dict[key] = None
		return games_dict

	def helper_teams():
		teams_list = []
		groups = ("A", "B", "C", "D", "E", "F", "G", "H")
		for group_letter in groups:
			for i in range(1,5):
				teams_list.append(group_letter + str(i))
		return teams_list
					

					


	
@login.user_loader
def load_user(id):
	return User.query.get(int(id))


