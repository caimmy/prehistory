# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-6-7'

import base64
from flask import url_for
from utils.encode_helper import ensure_bytes

def makeTipsPageUrl(_title, _content, _theme='info', _jumpurl=''):
    """
    构造提示信息页的跳转参数
    :param url:
    :param _title:
    :param _content:
    :param _jumpto:
    :param _theme:
    :return:
    """
    return url_for("TipsPage", title=base64.b64encode(ensure_bytes(_title)),
                   content=base64.b64encode(ensure_bytes(_content)),
                   theme=_theme, jumpUrl=_jumpurl)