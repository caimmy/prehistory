# _*_ coding:utf-8 _*_
'''
@author: caimmy@qq.com
@license: FREE

@contact: http://www.github.com/caimmy
@software: in ksg

@file: encode_helper.py
@time: 17-6-21 下午4:27
@desc:

'''

def ensure_string(s):
    """
    确保数据是字符串
    :param s:
    :return:
    """
    if isinstance(s, bytes):
        return s.decode('utf-8')
    return str(s)

def ensure_bytes(s):
    """
    确保数据是字节
    :param s:
    :return:
    """
    if isinstance(s, str):
        return s.encode('utf-8')
    return s