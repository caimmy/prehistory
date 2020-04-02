# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-5-5'

import os

DEBUG_MODE = True

# 是否开启访问日志
ACCESS_LOG_ON = True

# 百度地图API密钥
KEY_BAIDU_MAP = '5ee4aa34d7e4d3254c5458bb2225f806'

# 主数据库配置
_MYSQL_HOST_DEBUG = '127.0.0.1'
_MYSQL_PORT_DEBUG = 3306
_MYSQL_DB_DEBUG = 'prehistory'
_MYSQL_USER_DEBUG = 'arch'
_MYSQL_PWD_DEBUG = 'abcd1234'

# 图数据库配置
_NEO4J_HOST = 'bolt://www.prehistory.cn:7687'
_NEO4J_PASS = 'abcd1234'

SMTP_HOST = 'smtp.sina.com'
SMTP_PORT = 25
MAIL_USER = 'taoism_drawlot'
MAIL_SENDER = 'taoism_drawlot@sina.com'
MAIL_PWD = '12345678'