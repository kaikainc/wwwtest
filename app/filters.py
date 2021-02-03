import re
from datetime import datetime, timedelta

from . import utils
from . import settings

class Filter(object):
    def init_app(self, app):

        @app.add_template_filter
        def abbr(s):
            return utils.abbr(s)

        @app.add_template_filter
        def vabs(s):  
            if s is not None:
                return abs(s)
            else:
                return s

        @app.add_template_filter
        def display(s):
            if s is None:
                return ''
            else:
                return s
        
        @app.add_template_filter
        def female_or_male(s):
            if s == 1:
                return u'男'
            elif s == 0:
                return u'女'
            else:
                return ''

        @app.add_template_filter
        def ellipsis(s, length):
            if len(s) > length:
                return s[:length] + '...'
            else:
                return s

        @app.add_template_filter
        def abbr_agmt_name(s):
            return s[0:1] + '*'

        