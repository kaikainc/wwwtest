import re

from . import settings
from .calcdb import base

def abbr(s):
    if s is None or s == '':
        return ''

    try:
        if abs(s) >= 100000000:
            res = round(float(s)/100000000, 2)
            return str(res) + ' 亿'
        elif 10000 <= abs(s) < 100000000:
            res = round(float(s)/10000, 2)
            return str(res) + ' 万'
        else:
            return s
    except:
        return ''

def accum(v):
    '''计算列表连续累计值'''

    rec = []
    for i in range(len(v)):
        rec.append(sum(v[:i+1]))

    return rec

def is_valid_browser(useragent):
    '''检测浏览器'''

    patterns = [('[Ff]irefox.(\d+)(\.\d+)*', 52), ('[Cc]hrome.(\d+)(\.\d+)*', 49)]

    FOUND = False
    for pattern, version in patterns:
        UA = re.compile(pattern)
        
        match = UA.search(useragent)
        if match:
            FOUND = True
            s = match.group(0)
            v = s.split('/')[1].split('.')[0]

            if int(v) < version:
                return False, '浏览器: %s 版本较低'%(s,)
            else:
                return True, '检测通过'

    if not FOUND:
        return False, '浏览器不是Firefox或Chrome'

def get_near_date(datelist, d):
    '''获取日期列表中最近日期'''

    if d in datelist:
        return d

    diff = [abs((d-x).days) for x in datelist]

    m = diff[0]
    p = 0
    for i, k in enumerate(diff):
        if k < m:
            m = k
            p = i

    return datelist[p] 

def get_access_color(x):
    ACCESS = ["#eeeeee", "#d6e685", "#8cc665", "#44a340", "#1e6823"]
    
    if x == 0:
        return ACCESS[0]
    elif 0 < x <= 20:
        return ACCESS[1]
    elif 20 < x <= 40:
        return ACCESS[2]
    elif 40 < x <= 60:
        return ACCESS[3]
    elif x > 60:
        return ACCESS[4]

def is_allow_ip(ip, allow_ip):
    '''检测允许ip'''

    FOUND = False
    for pattern in allow_ip:
        x = re.compile(pattern)
        if x.search(ip):
            FOUND = True
            break
    
    return FOUND