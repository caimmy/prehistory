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
from gensim.models import Word2Vec

def application_path(*args):
    """
    构造相对于应用程序根路径的绝对路径
    :param args:
    :return:
    """
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root_path, *args)


def loadAllWord2vecModels():
    """
    加载所有词向量模型
    :return:
    """
    model_collection = {}
    file_list = os.listdir(application_path("ai", "models", "wordvector"))
    for mf in file_list:
        abs_position = application_path("ai", "models", "wordvector", mf)
        if mf.endswith("model") and os.path.isfile(abs_position):
            model_collection.setdefault(mf.split(".")[0], Word2Vec.load(abs_position))
    return model_collection
