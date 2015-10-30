__author__ = 'zhoufei'
from flask.ext.wtf import Form
from wtforms import StringField ,PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
	email = StringField('Email',validators=[Required(),Length(1,64),Email()])
	password = PasswordField('Password',validators=[Required()])
	remeber_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')
class RegistrationForm(Form):
	email = StringField('Email',validators=[Required(),Length(1,64),Email()])
	username = StringField('Username',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letter,''numbers,dot or underscores')])
	password = PasswordField('password',validators=[Required(),EqualTo('password2',message='Password must match')])
	password2 = PasswordField('Confirm password',validators=[Required()])
	submit = SubmitField('Register')

	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered')
	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already in use.')
class ChangePasswordForm(Form):
	old_password = PasswordField('Old password',validators=[Required()])
	password = PasswordField('New password',validators=[Required(),EqualTo('password2',message='Passwords must match')])
	password2 = PasswordField('Confirm new password',validators=[Required()])
	submit = SubmitField('Update Password')
class PasswordResetRequestForm(Form):
	email = StringField('Email',validators=[Required(),Length(1,64),Email()])
	submit = SubmitField('Reset Password')
class PasswordResetForm(Form):
	email = StringField('Email',validators=[Required(),Length(1,64),Email()])
	password = PasswordField('New password',validators=[Required(),EqualTo('password2',message='Passwords must match')])
	password2 = PasswordField('Confirm new password',validators=[Required()])
	submit = SubmitField('Reset Password')
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first() is None:
			raise ValidationError('Unknow email address.')
class ChangeEmailForm(Form):
	email = StringField('Email',validators=[Required(),Length(1,64),Email()])
	password = PasswordField('New password',validators=[Required(),EqualTo('password2',message='Passwords must match')])
	submit = SubmitField('Update Email Address')
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first() :
			raise ValidationError('Email already registered.')


