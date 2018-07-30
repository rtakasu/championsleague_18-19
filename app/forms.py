from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SubmitField, FieldList, FormField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, InputRequired, Optional
from app.models import User, Tournament

class BracketForm(FlaskForm): 
	winner = StringField('Winner', validators=[InputRequired()])
	submit = SubmitField('Submit Bracket')

class GameEntryForm(FlaskForm):
	home_result = IntegerField('Home', validators=[InputRequired()])
	away_result = IntegerField('Away', validators=[InputRequired()])

class GroupStageForm(FlaskForm):
	games = FieldList(FormField(GameEntryForm), min_entries=96)
	submit = SubmitField('Submit Group Stage Scores')

class R16StageForm(FlaskForm):
	games = FieldList(FormField(GameEntryForm), min_entries=16)
	submit = SubmitField('Submit R16 Scores')

class QFStageForm(FlaskForm):
	games = FieldList(FormField(GameEntryForm), min_entries=8)
	submit = SubmitField('Submit QF Scores')

class SFStageForm(FlaskForm):
	games = FieldList(FormField(GameEntryForm), min_entries=4)
	submit = SubmitField('Submit SF Scores')

class FStageForm(FlaskForm):
	games = FieldList(FormField(GameEntryForm), min_entries=1)
	submit = SubmitField('Submit F Scores')

class AdminGameEntryForm(FlaskForm):
	home_result = IntegerField('Home', validators=[Optional()])
	away_result = IntegerField('Away', validators=[Optional()])

class AdminGroupStageForm(FlaskForm):
	games = FieldList(FormField(AdminGameEntryForm), min_entries=96)
	submit = SubmitField('Submit Group Stage Scores')

class AdminR16StageForm(FlaskForm):
	games = FieldList(FormField(AdminGameEntryForm), min_entries=16)
	submit = SubmitField('Submit R16 Scores')

class AdminQFStageForm(FlaskForm):
	games = FieldList(FormField(AdminGameEntryForm), min_entries=8)
	submit = SubmitField('Submit QF Scores')

class AdminSFStageForm(FlaskForm):
	games = FieldList(FormField(AdminGameEntryForm), min_entries=4)
	submit = SubmitField('Submit SF Scores')

class AdminFStageForm(FlaskForm):
	games = FieldList(FormField(AdminGameEntryForm), min_entries=1)
	submit = SubmitField('Submit F Scores')

class AdminTeamEntryForm(FlaskForm):
	team = StringField('Team Name', validators=[InputRequired()])

# *** To Improve:
class GroupTeamForm(FlaskForm):
	teams = FieldList(FormField(AdminTeamEntryForm), min_entries=32)
	submit = SubmitField('Submit Group Teams')

class R16TeamForm(FlaskForm):
	teams = FieldList(FormField(AdminTeamEntryForm), min_entries=16)
	submit = SubmitField('Submit R16 Teams')

class QFTeamForm(FlaskForm):
	teams = FieldList(FormField(AdminTeamEntryForm), min_entries=8)
	submit = SubmitField('Submit QF Teams')

class SFTeamForm(FlaskForm):
	teams = FieldList(FormField(AdminTeamEntryForm), min_entries=4)
	submit = SubmitField('Submit SF Teams')

class FTeamForm(FlaskForm):
	teams = FieldList(FormField(AdminTeamEntryForm), min_entries=2)
	submit = SubmitField('Submit F Teams')

class LoginForm(FlaskForm): 
	username = StringField('Username', validators=[InputRequired()])
	password = PasswordField('Password', validators=[InputRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[InputRequired()])
	email = StringField('Email', validators=[InputRequired(), Email()])
	password = PasswordField('Password', validators=[InputRequired()])
	password2 = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address')