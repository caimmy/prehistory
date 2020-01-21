# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-6-8'

"""
附加装饰器
"""

from functools import wraps
from flask import redirect, url_for
from utils.security_helper import is_Guest
from utils.url_helper import makeTipsPageUrl

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_Guest():
            return redirect(makeTipsPageUrl('禁止访问', '该地址需要登录用户才能访问，请登录您的帐号后重新尝试！', 'danger', url_for('frontpage')))
        return f(*args, **kwargs)
    return decorated_function


def Singleton(cls):
    instance = {}
    @wraps(cls)
    def getinstance(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]

    return getinstance
