from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FieldList, FormField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Tournament

class BracketForm(FlaskForm): 
	winner = StringField('Winner', validators=[DataRequired()])
	submit = SubmitField('Submit Bracket')

class GameEntryForm(FlaskForm):
	game_result = StringField('Result', validators=[DataRequired()])

class GroupStageForm(FlaskForm):
	games = FieldList(FormField(GameEntryForm), min_entries=96)
	submit = SubmitField('Submit Group Stage')

class LoginForm(FlaskForm): 
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address')