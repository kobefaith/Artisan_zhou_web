__author__ = 'zhoufei'

from flask import render_template,redirect,request,url_for,flash
from flask.ext.login import login_user,logout_user,login_required
from . import auth
from ..models import User
from .forms import LoginForm
from .forms import RegistrationForm

@auth.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remeber_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid username or password')
	return render_template('auth/login.html',form=form)
@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('main.index'))
@auth.route('/register',method=['GET','POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,
		            username=form.username.data,
		            password=form.password.data)
		db.session.add(user)
		flash('you can now login.')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html',form=form)



