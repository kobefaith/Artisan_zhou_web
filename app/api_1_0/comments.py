__author__ = 'zhoufei'
from flask import jsonify,request,g,url_for,current_app
from .. import db
from ..models import Post,Permission,Comment
from . import api
from .decorators import permisssion_required

@api.route('/comments/')
def get_comments():
	page = request.args.get('page',1,type=int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
		page,per_page=current_app.config['ARTISAN_COMMENTS_PER_PAGE'],
		error_out=False	)
	comments = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('api.get_comments',page=page-1,_external=True)
