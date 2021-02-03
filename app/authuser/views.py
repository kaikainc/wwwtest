import os, os.path
import re
import urllib.request
import json

from datetime import datetime
from functools import update_wrapper

from PIL import Image

from . import authuser
from .. import db
from .. import vcode
from ..models import AuthUser, AnonymousUser
from .. import login_manager
from ..calcdb import base
from ..calcdb import utils as gutils
from .. import settings
from .. import utils, conv


from flask import render_template, redirect
from flask import request, url_for, session
from flask import make_response, current_app, abort

from flask_login import current_user, login_required, login_user, logout_user

login_manager.anonymous_user = AnonymousUser

LOGIN_ERRORS = (
    '刚才输入的密码错误!',
    '刚才输入的验证码错误!',
    '检测到你的电脑准备访问其他网点, 系统禁止这种行为!',
    '刚才输入的用户名不存在!',
    '刚才输入的用户不是代理金融网点!',
    '您使用的网络不是代理金融网络!',
    '请选择阅知并遵守保密协议',
    '输入的用户名不在内测用户范围内',
)
        
@authuser.before_app_request
def before_request():
    '''登录用户的最近访问时间'''

    if request.path == '/favicon.ico':
        return
        
    #针对nginx反向代理处理ip
    if current_user.is_authenticated:
        current_user.ping(request.headers.get('X-Forwarded-For', '')) 


#对验证码url进行处理
def nocache(f):
    def new_func(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        resp.cache_control.no_cache = True
        return resp
    return update_wrapper(new_func, f)

@login_manager.user_loader
def user_loader(user_id):
    return AuthUser.query.filter_by(id=user_id).first()

@authuser.route('/', methods=['GET', 'POST'])
def login():
    '''登录'''

    ip_addr = request.headers.get('X-Forwarded-For', '')

    next = request.args.get('next')
    if next:
        url = request.path + '?' + request.query_string.decode()
    else:
        url = request.path
    
    if request.method == 'GET':
        useragent = request.headers['User-Agent']
        valid, check_msg = utils.is_valid_browser(useragent)
        if not valid:
            return render_template('warning.html', check_msg=check_msg)

        if current_user.is_authenticated:
            return redirect(url_for('main.show_index'))
        else:
            return render_template('login.html', url=url)

    username = request.form['username']
    pwd = request.form['pwd']
    verifycode = request.form['verifycode']

    user = AuthUser.query.filter_by(username=username).first()

    if user is None:
        return render_template('login.html', 
            login_failed=True,
            login_error=LOGIN_ERRORS[3],
            url=url
        )

    x = request.cookies.get('auth_code', '')
    s = gutils.decrypt(settings.TOKEN, x)

    if (user.check_password(pwd) and verifycode.lower() == s):
        login_user(user)
        return redirect(next or url_for('main.show_index'))
    else:
        current_app.config['MYLOGGER'].error(
            '用户: %s, 输入口令: %s, 输入验证码: %s, session auth_code: %s', 
            username, pwd, verifycode, s
        )
        
        if not user.check_password(pwd):
            login_error = LOGIN_ERRORS[0]
        elif verifycode.lower() != s:
            login_error = LOGIN_ERRORS[1]
            
        return render_template('login.html', 
            login_failed=True,
            login_error=login_error,
            url=url
        )

@authuser.route('/logout')
def logout():
    '''退出'''

    logout_user()
    #session.pop('auth_code', None)
    return redirect(url_for('authuser.login'))

@authuser.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = vcode.gen_rand_str()
    return session['_csrf_token']

authuser.add_app_template_global(generate_csrf_token, 'csrf_token')

#验证码图片
@authuser.route('/makeimage')
def make_image():
    '''生成验证码图片'''

    s = vcode.gen_rand_str()
    c = vcode.make_image(current_app.config['IMAGE_FONT'], s)
    rsp = make_response(c.getvalue())
    rsp.mimetype = "image/jpeg"

    x = gutils.encrypt(settings.TOKEN, s)
    rsp.set_cookie('auth_code', x)

    return rsp

#水印背景
@authuser.route('/makewater')
def make_water():
    '''生成水印背景图片'''

    # s = vcode.gen_rand_str()
    # c = vcode.make_image(current_app.config['IMAGE_FONT'], s)

    ip_addr = request.headers.get('X-Forwarded-For')
    cc = current_user.username

    q = base.DB(settings.PG_DB)
    cc_name = q.get_cc_name(cc)

    if ip_addr is not None:
        text = [ip_addr, cc_name]
    else:
        text = [cc_name]

    s = vcode.center_text(text)
    c = vcode.add_text_to_image(current_app.config['IMAGE_FONT'], s)

    rsp = make_response(c.getvalue())
    rsp.mimetype = "image/png"

    return rsp  