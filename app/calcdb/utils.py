import re
import bisect

from cryptography.fernet import Fernet
from datetime import datetime
from decimal import Decimal

def encrypt(token: str, acc: str) -> str:
    '''加密'''

    f = Fernet(token.encode())
    return f.encrypt(acc.encode()).decode()

def decrypt(token: str, enc_acc: str) -> str:
    '''解密'''

    f = Fernet(token.encode())
    return f.decrypt(enc_acc.encode()).decode()

def extract(pid):
    '''分解身份证号提取出生日期、性别、年龄'''

    if pid is None:
        return None, None, None

    id = pid.strip()

    if len(id) == 18:
        try:
            x = datetime.strptime(id[6:14], '%Y%m%d')
        except:
            return None, None, None

        try:
            birth, sex, age = id[6:14], int(id[16]) % 2, datetime.today().year - x.year
        except:
            birth, sex, age = id[6:14], None, datetime.today().year - x.year
    elif len(id) == 15:
        try:
            x = datetime.strptime('19'+id[6:12], '%Y%m%d')
        except:
            return None, None, None

        if id[14] == 'X':
            #存在最后一位是X，无法判定性别
            birth, sex, age = id[6:12], None, datetime.today().year - x.year
        else:
            birth, sex, age = id[6:12], int(id[14]) % 2, datetime.today().year - x.year
    else:
        birth, sex, age = None, None, None
    return birth, sex, age

