import os
import json
from flask import Flask, redirect, url_for, session, request, jsonify, Markup
from flask_oauthlib.client import OAuth

RR_APP_ID = os.environ.get('RENREN_APP_ID')
RR_APP_KEY = os.environ.get('RENREN_APP_KEY')

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

renren = oauth.remote_app(
    'renren',
    consumer_key='d6262e9fe5be47adaaeb7fb7a6903e46',
    consumer_secret='143e08f60cb3451bb5e451b068581b66',
    base_url='https://graph.renren.com',
    request_token_url=None,    
    access_token_url='/oauth/token',
    authorize_url='/oauth/authorize'
)


@app.route('/user_info')
def get_user_info():
    if 'renren_token' in session:
        return redirect(session['user']['avatar'][0]['url'])        
    return redirect(url_for('login'))


@app.route('/third_login/renren')
def login():
    return renren.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('renren_token', None)
    return redirect(url_for('get_user_info'))


@app.route('/login/authorized')
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
    return redirect(url_for('get_user_info'))


@renren.tokengetter
def get_renren_oauth_token():
    return session.get('renren_token')


if __name__ == '__main__':
    app.run()
