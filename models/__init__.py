# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-5-5'


from config import DEBUG_MODE, _MYSQL_DB_DEBUG, _MYSQL_HOST_DEBUG, _MYSQL_PORT_DEBUG, _MYSQL_PWD_DEBUG, _MYSQL_USER_DEBUG
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


if DEBUG_MODE:
    from config import _MYSQL_DB_DEBUG as MYSQL_DB, _MYSQL_HOST_DEBUG as MYSQL_HOST, _MYSQL_PWD_DEBUG as MYSQL_PASS, \
        _MYSQL_USER_DEBUG as MYSQL_USER, _MYSQL_PORT_DEBUG as MYSQL_PORT
else:
    try:
        from sae.const import (MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER, MYSQL_PORT)
    except Exception as e:
        print(str(e))


mysql_master_engine = create_engine("mysql+pymysql://%s:%s@%s:%d/%s?charset=utf8" % \
                              (MYSQL_USER, MYSQL_PASS, MYSQL_HOST, int(MYSQL_PORT), MYSQL_DB),
                                    pool_size=100, pool_recycle=3600, echo=DEBUG_MODE)


db_session = scoped_session(sessionmaker(bind=mysql_master_engine))
Base = declarative_base()
c


class SQLExtHelper:
    '''
    通过多继承方式使数据表类支持toDict操作
    '''
    def toDict(self):
        attributes = {}
        for _k in self.__mapper__.c.keys():
            _v = getattr(self, _k)
            if _v is None: _v = ''
            attributes[_k] = _v if type(_v) in [int, float, long] else str(_v)
        return attributes