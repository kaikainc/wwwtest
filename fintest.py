import os, os.path
import click

from app import create_app, db
from app.models import AuthUser
from app.calcdb import base
from app import settings

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.cli.command()
def create_db():
    #创建数据库
    db.create_all()

@app.cli.command()
@click.option('--username', default=None,
              help='重置用户口令')
def reset_auth_user(username):
    '''重置用户口令'''

    u = AuthUser.query.filter_by(username=username).first()
    if u is not None:
        u.set_password('123456')
    db.session.commit()

@app.cli.command()
@click.option('--username', default=None,
              help='用户名')
@click.option('--password', default=None,
              help='口令')
def change_password(username, password):
    '''更改指定用户口令'''

    u = AuthUser.query.filter_by(username=username).first()
    if u is not None:
        u.set_password(password)
    db.session.commit()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, AuthUser=AuthUser)