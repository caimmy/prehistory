# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-5-5'

from models import mysql_master_engine
from models.trunck import *


if __name__ == "__main__":
    Base.metadata.create_all(mysql_master_engine)
    print("init db successful")