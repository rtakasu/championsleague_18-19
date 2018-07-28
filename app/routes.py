from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, BracketForm, GroupStageForm, AdminTeamForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Tournament
from werkzeug.urls import url_parse
from sqlalchemy import desc

@app.route('/')
@app.route('/index')
def index():
	posts=Post.query.order_by(desc('timestamp')).all()
	return render_template('index.html', posts=posts)

@app.route('/submit_bracket', methods=['GET', 'POST'])
@login_required
def submit_bracket():
	form = BracketForm()
	
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
		post = Post(user_id=current_user.id, points=0)
		post.set_bracket({'winner': form.winner.data})
		post.make_valid()
		cl.calculate_points_specific(post)
		db.session.add(post)
		db.session.commit()
		flash('Congratulations you submitted a bracket')
		app.logger.info('Congratulations you submitted a bracket')
		return redirect(url_for('submit_bracket'))
	return render_template('submit_bracket.html', title='Submit Bracket', form=form)

@app.route('/submit_group_stage', methods=['GET', 'POST'])
@login_required
def submit_group_stage():
	group_games_labels = Tournament.helper_group_stage()
	form = GroupStageForm()
	
	labels_and_form_items = zip(group_games_labels, form.games)

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
		post = Post(user_id=current_user.id, points=0)
		games_guess_dict = {}
		for game_guess in labels_and_form_items:
			games_guess_dict[game_guess[0]] = game_guess[1].data["game_result"]
		print(games_guess_dict)
		post.set_group_guess(games_guess_dict)
		post.make_valid()
		cl.calculate_points_specific(post)
		db.session.add(post)
		db.session.commit()
		flash('Congratulations you submitted a bracket')
		app.logger.info('Congratulations you submitted a bracket')
		return redirect(url_for('submit_group_stage'))
	
	return render_template('submit_group_stage.html', title='Submit Group Stage', form=form, labels_and_form_items=labels_and_form_items)


@app.route('/profile')
@login_required
def profile():
	posts=Post.query.filter_by(user_id=current_user.id).order_by(desc('timestamp')).all()
	return render_template('profile.html', posts=posts)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
	form = BracketForm()

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
		cl.set_games({'winner':form.winner.data})
		db.session.commit()
		app.logger.info('Updated Tournament')
		return redirect(url_for('admin'))
	posts = Post.query.order_by(desc('points')).all()
	return render_template('admin.html', title='Admin', form=form, tournament=cl, posts=posts)

@app.route('/admin_submit_teams', methods=['GET', 'POST'])
@login_required
def admin_submit_teams():
	group_team_labels = Tournament.helper_teams()
	form = AdminTeamForm()

	labels_and_form_items = zip(group_team_labels, form.teams)

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
		cl.set_R16_teams(teams_dict)
		print(teams_dict)
		db.session.commit()
		app.logger.info('Updated Tournament')
		return redirect(url_for('admin_submit_teams'))
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
