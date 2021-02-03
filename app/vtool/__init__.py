from flask import Blueprint

vtool = Blueprint('vtool', __name__)

from . import views