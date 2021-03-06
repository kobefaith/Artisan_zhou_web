#-*-encoding: UTF-8 -*-
__author__ = 'zhoufei'

from flask import render_template,redirect,request,url_for,flash
from flask.ext.login import login_user,logout_user,login_required
from . import auth
from ..models import User
from .forms import LoginForm
from .forms import RegistrationForm
from .forms import Third_RegistrationForm
from .forms import ChangeEmailForm,ChangePasswordForm,PasswordResetRequestForm,PasswordResetForm
from ..email import send_email
from flask.ext.login import current_user
from .. import db
from .. import oauth
import os
from flask import session
@auth.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
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
@auth.route('/register',methods=['GET','POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,
		            username=form.username.data,
		            password=form.password.data,
		            image=url_for('static',filename='default.jpg',_external=True))
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email,'Confirm Your Account','auth/email/confirm',user=user,token=token)
		flash('A confirmation email has been sent to you by email')
		return redirect(url_for('main.index'))
	return render_template('auth/register.html',form=form)
@auth.route('/third_register',methods=['GET','POST'])
def third_register():
	form = Third_RegistrationForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if (user):
			login_user(user,True)
			return redirect(url_for('main.index'))
		user = User(email=form.email.data,
		            username=form.username.data,
		            image=session['user']['avatar'][0]['url'])
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email,'Confirm Your Account','auth/email/confirm',user=user,token=token)
		flash('A confirmation email has been sent to you by email')
		login_user(user,True)
		return redirect(url_for('main.index'))
	return render_template('auth/third_register.html',form=form)
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You have confirmed your account .Thanks!')
	else:
		flash('The confirmation link is invalid or has expired.')
	return redirect(url_for('main.index'))
@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed \
			and request.endpoint[:5] != 'auth.'\
			and request.endpoint !='static':
			return redirect(url_for('auth.unconfirmed'))
@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')
@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email,'Confirm Your Account',
	           'auth/email/confirm',user=current_user,token=token)
	flash('A new confirmation email has been sent to you by email.')
	return redirect(url_for('main.index'))
@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			flash('Your password has been updated.')
			return redirect(url_for('main.index'))
		else:
			flash('Invalid password.')
	return render_template("auth/change_password.html",form=form)
@auth.route('/reset',methods=['GET','POST'])
def password_reset_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_confirmation_token()
			send_email(user.email,'Reset Your Password',
			           'auth/email/reset_password',
			           user=user,token=token,
			           next=request.args.get('next'))
		flash('An email with instructions to reset your password has been '
		      'send to you .')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html',form=form)
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
@auth.route('/change-email',methods=['GET','POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)
@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))

RR_APP_ID = os.environ.get('RENREN_APP_ID')
RR_APP_KEY = os.environ.get('RENREN_APP_KEY')

renren = oauth.remote_app(
    'renren',
    consumer_key=RR_APP_ID,
    consumer_secret=RR_APP_KEY,
    base_url='https://graph.renren.com',
    request_token_url=None,
    access_token_url='/oauth/token',
    authorize_url='/oauth/authorize'
)


@auth.route('/user_info')
def get_user_info():
    if 'renren_token' in session:
	    return redirect(url_for('auth.third_register'))
        #return redirect(session['user']['avatar'][0]['url'])
    return redirect(url_for('auth.login'))


@auth.route('/third_login/renren')
def third_login():
    return renren.authorize(callback=url_for('auth.authorized', _external=True))


@auth.route('/third_logout')
@login_required
def third_logout():
    session.pop('renren_token', None)
    return redirect(url_for('auth.get_user_info'))


@auth.route('/login/authorized')
def authorized():
    resp = renren.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['renren_token'] = (resp['access_token'], '')

    # Get openid via access_token, openid and access_token are needed for API calls
    if isinstance(resp, dict):
        session['user'] = resp.get('user')
    return redirect(url_for('auth.get_user_info'))


@renren.tokengetter
def get_renren_oauth_token():
    return session.get('renren_token')









