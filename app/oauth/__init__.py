__author__ = 'zhoufei'
from flask import Blueprint
from flask_oauthlib.client import OAuth
oauth = Blueprint('oauth',__name__)

from . import views
