import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'testtesttest'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SSL_ENABLE = False
    IMAGE_FONT = os.path.join(basedir, 'app/static/font/wqy-microhei.ttc')

    INITDATA_PATH = os.path.join(basedir, 'initdata')

    LOG_PATH = os.path.join(basedir, 'logs')
    LOG_PATH_ERROR = os.path.join(LOG_PATH, 'errors.log')
    MYLOGGER = logging.getLogger("fin-logger")
    MYLOGGER.setLevel(logging.ERROR)

    LOCK_FILE = os.path.join(LOG_PATH, 'status.lock')

    SQLALCHEMY_DATABASE_URI = "postgresql://test:test@127.0.0.1/mydb"

    @classmethod
    def init_app(cls, app):
        if not os.path.exists(cls.LOG_PATH):
            os.mkdir(cls.LOG_PATH)

        handler = logging.FileHandler(cls.LOG_PATH_ERROR)
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(message)s"))
        cls.MYLOGGER.addHandler(handler)

class DevelopmentConfig(Config):
    DEBUG = True
    

class ProductionConfig(Config):
    SSL_ENABLE = bool(os.environ.get('SSL_ENABLE'))

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': ProductionConfig
}
