from flask import Blueprint

authuser = Blueprint('authuser', __name__)

from . import views
