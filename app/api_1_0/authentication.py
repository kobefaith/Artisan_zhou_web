__author__ = 'zhoufei'
from flask import g,jsonify
from flask.ext.httpauth import HTTPBasicAuth
from ..models import User,AnonymousUser
from . import api
from .errors import unauthorized,forbidden

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token,password):
	if email_or_token == '':
		g.current_user = AnonymousUser()
		return True
	if password == '':
		g.current_user = User.verify_auth_token(email_or_token)
		g.token_used = True
		return g.current_user is not None
	if not user:
		return False
	g.current_user = user
	g.token_used = False
	return user.verify_password(password)
@auth.error_handler
def auth_error()
	return unauthorized('Invalid credentials')

