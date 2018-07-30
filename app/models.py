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

	def set_guess(self, game_stage, guess):
		if game_stage == "group":
			self.group_stage_guess = pickle.dumps(guess)
		elif game_stage == "R16":
			self.R16_guess = pickle.dumps(guess)
		elif game_stage == "QF":	
			self.QF_guess = pickle.dumps(guess)
		elif game_stage == "SF":
			self.SF_guess = pickle.dumps(guess)
		elif game_stage == "F":
			self.F_guess = pickle.dumps(guess)

	def get_guess(self, game_stage):
		if game_stage == "group" and self.group_stage_guess:
			return pickle.loads(self.group_stage_guess)
		elif game_stage == "R16" and self.R16_guess:
			return pickle.loads(self.R16_guess)
		elif game_stage == "QF" and self.QF_guess:	
			return pickle.loads(self.QF_guess)
		elif game_stage == "SF" and self.SF_guess:
			return pickle.loads(self.SF_guess)
		elif game_stage == "F" and self.F_guess:
			return pickle.loads(self.F_guess)
		return None


	def set_game_points(self, game_stage, game, points):
		current_guess = self.get_guess(game_stage)
		current_guess[game]["points"] = points
		self.set_guess(game_stage, current_guess)
		
	def make_valid(self):
		posts = Post.query.filter(id!=self.id).all()
		for post in posts:
			post.valid = False
		self.valid = True

class Tournament(db.Model):
	id = db.Column(db.Integer, primary_key=True)

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

	def set_teams(self, game_stage, teams):
		if game_stage == "group":
			self.group_stage_teams = pickle.dumps(teams)
		elif game_stage == "R16":
			self.R16_teams = pickle.dumps(teams)
		elif game_stage == "QF":	
			self.QF_teams = pickle.dumps(teams)
		elif game_stage == "SF":
			self.SF_teams = pickle.dumps(teams)
		elif game_stage == "F":
			self.F_teams = pickle.dumps(teams)

	def set_games(self, game_stage, games):
		if game_stage == "group":
			self.group_stage_games = pickle.dumps(games)
		elif game_stage == "R16":
			self.R16_games = pickle.dumps(games)
		elif game_stage == "QF":	
			self.QF_games = pickle.dumps(games)
		elif game_stage == "SF":
			self.SF_games = pickle.dumps(games)
		elif game_stage == "F":
			self.F_game = pickle.dumps(games)

	def get_teams(self, game_stage):
		if game_stage == "group" and self.group_stage_teams:
			return pickle.loads(self.group_stage_teams)
		elif game_stage == "R16" and self.R16_teams:
			return pickle.loads(self.R16_teams)
		elif game_stage == "QF" and self.QF_teams:	
			return pickle.loads(self.QF_teams)
		elif game_stage == "SF" and self.SF_teams:
			return pickle.loads(self.SF_teams)
		elif game_stage == "F" and self.F_teams:
			return pickle.loads(self.F_teams)
		return None

	def get_games(self, game_stage):
		if game_stage == "group" and self.group_stage_games:
			return pickle.loads(self.group_stage_games)
		elif game_stage == "R16" and self.R16_games:
			return pickle.loads(self.R16_games)
		elif game_stage == "QF" and self.QF_games:	
			return pickle.loads(self.QF_games)
		elif game_stage == "SF" and self.SF_games:
			return pickle.loads(self.SF_games)
		elif game_stage == "F" and self.F_game:
			return pickle.loads(self.F_game)
		return None

	def calculate_points(self):
		posts = Post.query.all()
		for post in posts:
			self.calculate_points_specific(post)

	def calculate_points_specific(self, post):
		# Takes in post instance and calculates (and saves) its points 
		# based on the game results saved in the tournament object
		# for result in post.get_group_stage():
		
		game_results = self.get_games("group") # *** To Update
		guess_results = post.get_guess("group") # *** To Update
		points = 0

		if game_results and guess_results:
			for game_label in game_results:
				
				if game_results[game_label]["played"]:
					
					# if exact score => 3 points
					if game_results[game_label]["result"] == guess_results[game_label]["result"]:
						points += 3
						post.set_game_points("group", game_label, 3)
						continue

					# if correct result but wrong score => 1 point
					game_winner = Tournament.helper_winner(game_results[game_label]["result"])
					guess_winner = Tournament.helper_winner(guess_results[game_label]["result"])

					if game_winner == guess_winner:
						post.set_game_points("group", game_label, 1)
						points += 1
					else:
						post.set_game_points("group", game_label, 0)


		post.points = points


	def helper_game_labels(game_stage):
		# Returns a dict of games and their results.
		# Keys are the teams that are facing each other, 
		# ex: {'A1HvsA2A': {'result':None, 'played':None},... } in group stage 

		games_dict = {}
		groups = Tournament.helper_groups(game_stage)

		for group in groups:
			for home_team in groups[group]:
				for away_team in groups[group]:
					if home_team != away_team:
						key = home_team + "H" + "vs" + away_team + "A"
						games_dict[key] = {'result': None, 'played': None}
						if game_stage == "F":
							return games_dict
		return games_dict



	def helper_groups(game_stage):
		# Returns a dict of groups with labels of teams in each group
		# Group stage: {'A': ['A1','A2',...], 'B': ['B1','B2',...],...}
		# Knockout stage: Treat each knockout stage as a group with 2 teams

		groups = {}
		teams_per_group = 2
		groups_list = []
		if game_stage == "group":
			groups_list = ["A", "B", "C", "D", "E", "F", "G", "H"]
			teams_per_group = 4
		elif game_stage == "R16":
			groups_list = ["R16_A", "R16_B", "R16_C", "R16_D", "R16_E", "R16_F", "R16_G", "R16_H"]
		elif game_stage == "QF":
			groups_list = ["QF_A", "QF_B", "QF_C", "QF_D"]
		elif game_stage == "SF":
			groups_list = ["SF_A", "SF_B"]
		elif game_stage == "F":
			groups_list = ["F"]

		for group_letter in groups_list:
				teams_list = []
				for i in range(1,teams_per_group+1):
					teams_list.append(group_letter + str(i))
				groups[group_letter] = teams_list

		return groups

	def helper_winner(score):
		# Returns whether home (won), away (won) or draw based on the input score string
		# Ex: 
		# 3vs1 -> home
		# 0vs2 -> away
		# 2vs2 -> draw
		home_score = score[0:1]
		away_score = score[3:4]
		if home_score > away_score:
			return "home"
		elif home_score < away_score:
			return "away"
		else:
			return "draw"

	def helper_parse_game_label(game_label):
		# Input: Game label in the form A1HvsA2A or R16_A1HvsR16_A2A
		# Output: Dict: {'home_team': 'A1', 'away_team':'A2'}

		vs_index = None
		i = 0
		for char in game_label:
			if char == 'v':
				vs_index = i
			i+=1
		home_team = game_label[0:vs_index-1]
		away_team = game_label[vs_index+2:-1]
		return {"home_team": home_team, "away_team": away_team}

	
@login.user_loader
def load_user(id):
	return User.query.get(int(id))


