# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： apptools
@Description:
@Author: caimmy
@date： 2020/1/13 17:06
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""

import os

def application_path(*args):
    """
    构造相对于应用程序根路径的绝对路径
    :param args:
    :return:
    """
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root_path, *args)
