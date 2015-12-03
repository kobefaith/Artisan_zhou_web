__author__ = 'zhoufei'
from flask import jsonify,request,g,abort,url_for,current_app
from .. import db
from ..models import Post,Permission
from . import api
from .decorators import permission_required
from .errors import forbidden

@api.route('/posts')
@auth.login_required
def get_posts():
	posts = Post.query.all()
	return jsonify({'posts':[post.to_json() for post in posts]})

@api.route('/posts/<int:id>')
@auth.login_required
def get_post(id):
	post = Post.query.get_or_404(id)
	return jsonify(post.to_json())

