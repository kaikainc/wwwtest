from datetime import date, datetime, timedelta

from flask import render_template
from flask_login import login_required, current_user

from . import main

from ..calcdb import base

from .. import settings
from .. import utils
from .. import conv

@main.route("/index")
@login_required
def show_index():
    '''首页'''

    cc = current_user.username
    b = base.DB(settings.PG_DB)

    return render_template(
        'index.html',
        cc=cc,

    )

@main.route("/main/home")
@login_required
def home():
    '''业务概览'''
    
    cc = current_user.username
    b = base.DB(settings.PG_DB)

    return render_template(
        'home.html',
        cc=cc,

    )
