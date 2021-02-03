from flask import render_template
from flask_login import login_required, current_user
from flask import request, jsonify
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from . import vtool

from .. import db
from ..calcdb import ck, base, cass, vis

from .. import settings
from .. import utils
from .. import conv

from ..calcdb import utils as gutils

@vtool.route('/tool/changepassword', methods=['GET', 'POST'])
@login_required
def change_passwd():
    '''修改密码'''
    
    cc = current_user.username
    q = base.DB(settings.PG_DB)
    cc_name = q.get_cc_name(cc)

    q.close()

    if request.method == 'GET':
        return render_template(
            'tool/password.html',
            cc_name=cc_name)

    if  request.method == 'POST':  
        pwdold = request.form['pwdold']
        pwdnew = request.form['pwdnew']
        pwdconfirm = request.form['pwdconfirm']

        if pwdnew.strip() == '':
            msg = '密码不能为空'
            return render_template(
                'tool/password.html',
                cc_name=cc_name,
                succ=msg)

        ##核对原密码是否正确
        if current_user.check_password(pwdold):  
            ##核对新密码的两次输入是否一致
            if pwdnew == pwdconfirm:
                current_user.set_password(pwdnew)
                db.session.commit()
                msg = '修改成功'
                return render_template(
                    'tool/password.html',
                    cc_name=cc_name,
                    succ=msg)
            else:
                msg = '两次密码输入不一致'              
                return render_template(
                    'tool/password.html',
                    cc_name=cc_name,
                    msg=msg)
        else:
            msg = '原密码输入不正确'
            return render_template(
                'tool/password.html',
                cc_name=cc_name,
                msg=msg)

@vtool.route("/tool/show_etl_job_log")
@login_required
def show_etl_job_log():
    '''下载平台etl增量表日志'''

    cc = current_user.username

    q = base.DB(settings.PG_DB)
    cc_name = q.get_cc_name(cc)
    results = q.get_etl_job_log()

    conv.add_etl_table_cnname(results, settings.ETL_TABLES)

    q.close()

    return render_template(
        'tool/show_etl_job_log.html',
        cc_name=cc_name,
        results=results
    )

@vtool.route('/tool/show_access_log')
@login_required
def show_access_log():
    '''访问日志'''

    cc = current_user.username

    q = vis.VisDB(settings.PG_DB)

    cc_name = q.get_cc_name(cc)
    visitors = q.get_brch_visit(cc)

    q.close()

    c = ck.CcCKLog(settings.CK_CONN)
    d1 = datetime.now()
    d2 = d1 - timedelta(days=15)
    end_date, start_date = d1.strftime('%Y-%m-%d'), d2.strftime('%Y-%m-%d')

    everyday_cnt = c.total_everyday_access_cnt(cc, start_date, end_date)

    c.close()

    for brch, details in everyday_cnt.items():
        #补日期空白
        k = d2
        all_access_date = [x['access_date'] for x in details]
        
        while k.strftime('%Y-%m-%d') <= end_date:
            if k.date() not in all_access_date:
                d = dict()
                d['access_date'] = k.date()
                d['cnt'] = 0

                details.append(d)
            
            k = k + timedelta(days=1)

        #补颜色对应值
        for x in details:
            x['color'] = utils.get_access_color(x['cnt'])

        details.sort(key=lambda x: x['access_date'])

    today = datetime.today().strftime("%Y%m%d")
    #补充3个key: pwd_status, today_status, details(access_date, cnt)
    for x in visitors:
        if check_password_hash(x['pwdhash'], 'jxyz-'+x['brch_code'][4:]):
            x['pwd_status'] = False
        else:
            x['pwd_status'] = True

        if x['last_seen'] is not None and x['last_seen'].strftime("%Y%m%d") == today:
            x['today_status'] = True
        else:
            x['today_status'] = False

        if x['brch_code'] in everyday_cnt:
            x['details'] = everyday_cnt[x['brch_code']]
        else:
            x['details'] = []

    return render_template(
        "tool/show_access_log.html",
        cc_name=cc_name,
        visitors=visitors,
        access_color=settings.ACCESS_COLOR, 
        end_date=end_date,
    )

@vtool.route("/tool/reset_user/<username>")
@login_required
def reset_user(username: str):
    '''重置用户密码'''

    password = 'jxyz-' + username[-4:]
    pwdhash = generate_password_hash(password)

    q = vis.VisDB(settings.PG_DB)
    q.reset_pwd(username, pwdhash)

    q.close()

    return jsonify({
        'status': True,
    })

@vtool.route('/tool/show_access_log_detail/<brch>/<access_date>')
@login_required
def show_access_log_detail(brch, access_date):
    '''网点访问日志详情'''

    q = base.DB(settings.PG_DB)
    brch_name = q.get_brch_name(brch, settings.SPEC_BRCH)

    c = ck.BrchCKLog(settings.CK_CONN)
    access_log = c.get_access_log(brch, access_date, settings.TOKEN)
    ip_cnt = c.total_ip_access_cnt(brch, access_date)
    desc_cnt = c.total_desc_access_cnt(brch, access_date)

    c.close()

    return render_template(
        "tool/show_access_log_detail.html",

        brch_name=brch_name,
        access_date=access_date,
        access_log=access_log,
        ip_cnt=ip_cnt,
        desc_cnt=desc_cnt,
    )