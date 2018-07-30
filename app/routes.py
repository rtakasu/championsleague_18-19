from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, BracketForm
from app.forms import GroupStageForm, R16StageForm, QFStageForm, SFStageForm, FStageForm
from app.forms import GroupTeamForm, R16TeamForm, QFTeamForm, SFTeamForm, FTeamForm 
from app.forms import AdminGroupStageForm, AdminR16StageForm, AdminQFStageForm, AdminSFStageForm, AdminFStageForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Tournament
from werkzeug.urls import url_parse
from sqlalchemy import desc

@app.route('/')
@app.route('/index')
def index():
	posts=Post.query.order_by(desc('timestamp')).all()
	return render_template('index.html', posts=posts)

@app.route('/submit_scores/<string:game_stage>', defaults={'post_id': None}, methods=['GET', 'POST'])
@app.route('/submit_scores/<string:game_stage>/<string:post_id>', methods=['GET', 'POST'])
@login_required
def submit_scores(game_stage, post_id):
	game_labels = Tournament.helper_game_labels(game_stage)
	
	if game_stage == "group":
		form = GroupStageForm()
	elif game_stage == "R16":
		form = R16StageForm()
	elif game_stage == "QF":
		form = QFStageForm()
	elif game_stage == "SF":
		form = SFStageForm()
	elif game_stage == "F":
		form = FStageForm()
	
	labels_and_form_items = zip(game_labels, form.games)

	# Retrieve CL tournament
	tournaments = Tournament.query.all()
	if len(tournaments) != 0:
		cl = tournaments[0]
	else: 
		cl = Tournament()
		db.session.add(cl)
	cl.calculate_points()
	db.session.commit()


	games_info = {}
	teams_dict = cl.get_teams(game_stage) 
	if teams_dict:	
		for game_label in game_labels:
			temp = Tournament.helper_parse_game_label(game_label)
			games_info[game_label] = {"home_team": teams_dict[temp["home_team"]], "away_team": teams_dict[temp["away_team"]]}


	if form.validate_on_submit():
		if post_id:
			post = Post.query.filter_by(id=post_id).all()[0]
		else:
			post = Post(user_id=current_user.id, points=0)
		games_guess_dict = {}
		for game_guess in labels_and_form_items:
			games_guess_dict[game_guess[0]] = str(game_guess[1].data["home_result"]) + "vs" + str(game_guess[1].data["away_result"])
			games_guess_dict[game_guess[0]] = {
					"result": str(game_guess[1].data["home_result"]) + "vs" + str(game_guess[1].data["away_result"]),
					"points": 0
					}
		post.set_guess(game_stage, games_guess_dict)
		post.make_valid()
		cl.calculate_points_specific(post)
		db.session.add(post)
		db.session.commit()
		flash('Congratulations you submitted a bracket')
		app.logger.info('Congratulations you submitted a bracket')
		return redirect(url_for('submit_scores', game_stage=game_stage, post_id=post.id))
	
	return render_template('submit_scores.html', title='Submit Group Stage', form=form, labels_and_form_items=labels_and_form_items, games_info=games_info)


@app.route('/profile')
@login_required
def profile():
	posts=Post.query.filter_by(user_id=current_user.id).order_by(desc('timestamp')).all()
	return render_template('profile.html', posts=posts)

@app.route('/admin_submit_scores/<string:game_stage>', methods=['GET', 'POST'])
@login_required
def admin_submit_scores(game_stage):
	game_labels = Tournament.helper_game_labels(game_stage)

	if game_stage == "group":
		form = AdminGroupStageForm()
	elif game_stage == "R16":
		form = AdminR16StageForm()
	elif game_stage == "QF":
		form = AdminQFStageForm()
	elif game_stage == "SF":
		form = AdminSFStageForm()
	elif game_stage == "F":
		form = AdminFStageForm()

	labels_and_form_items = zip(game_labels, form.games)

	# Retrieve CL tournament
	tournaments = Tournament.query.all()
	if len(tournaments) != 0:
		cl = tournaments[0]
	else: 
		cl = Tournament()
		db.session.add(cl)
	cl.calculate_points()
	db.session.commit()

	games_info = {}
	teams_dict = cl.get_teams(game_stage)

	if teams_dict:	
		for game_label in game_labels:
			temp = Tournament.helper_parse_game_label(game_label)
			games_info[game_label] = {"home_team": teams_dict[temp["home_team"]], "away_team": teams_dict[temp["away_team"]]}
	
	if form.validate_on_submit():
		games_dict = {}
		for game in labels_and_form_items:
			games_dict[game[0]] = {
					"result": str(game[1].data["home_result"]) + "vs" + str(game[1].data["away_result"]),
					"played": (game[1].data["home_result"] != None and game[1].data["home_result"] != None)
					}
		print(games_dict)
		cl.set_games(game_stage, games_dict)
		db.session.commit()
		app.logger.info('Updated Tournament')
		return redirect(url_for('admin_submit_scores', game_stage=game_stage))
	else:
		print("form not valid")
	posts = Post.query.order_by(desc('points')).all()
	return render_template('admin_submit_scores.html', title='Admin', form=form, tournament=cl, labels_and_form_items=labels_and_form_items, games_info=games_info, game_stage=game_stage)


@app.route('/admin_submit_teams/<string:game_stage>', methods=['GET', 'POST'])
@login_required
def admin_submit_teams(game_stage):
	groups = Tournament.helper_groups(game_stage)
	team_labels_list = []
	for group in groups:
		team_labels_list += groups[group]

	if game_stage == "group":
		form = GroupTeamForm()
	elif game_stage == "R16":
		form = R16TeamForm()
	elif game_stage == "QF":
		form = QFTeamForm()
	elif game_stage == "SF":
		form = SFTeamForm()
	elif game_stage == "F":
		form = FTeamForm()

	labels_and_form_items = zip(team_labels_list, form.teams)

	# Retrieve CL tournament
	tournaments = Tournament.query.all()
	if len(tournaments) != 0:
		cl = tournaments[0]
	else: 
		cl = Tournament()
		db.session.add(cl)
	cl.calculate_points()
	db.session.commit()
	
	if form.validate_on_submit():
		teams_dict = {}
		for team_assignment in labels_and_form_items:
			teams_dict[team_assignment[0]] = team_assignment[1].data["team"]
		cl.set_teams(game_stage, teams_dict)
		print(teams_dict)
		db.session.commit()
		app.logger.info('Updated Tournament')
		return redirect(url_for('admin_submit_teams', game_stage=game_stage))
	posts = Post.query.order_by(desc('points')).all()
	return render_template('admin_submit_teams.html', title='Admin', form=form, tournament=cl, labels_and_form_items=labels_and_form_items)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			app.logger.info('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations you are a registered user')
		app.logger.info('New User created')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/shutdown')
def shutdown():
	db.session.close()
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()
	return 'Server shutting down...'
