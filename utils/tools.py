# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-5-7'

import json

CODE_SUCCESS = 0
CODE_FAILURE = -1

RESPONSE_TYPE = 'json'

def getFailureResponse():
    """
    获取失败的数据响应
    :return: dict
    """
    return {
        'code': CODE_FAILURE,
        'msg': 'unkown',
        'success': False
    }


def changeResponseToSuccess(ret_info):
    """
    转换失败的错误响应为成功
    :param ret_info: dict
    :return: dict
    """
    ret_info['code'] = CODE_SUCCESS
    ret_info['success'] = True
    return ret_info

def setResponseData(ret_info, _data):
    """

    :param ret_info:
    :param _data:
    :return:
    """
    ret_info['data'] = _data
    return ret_info

def makeResponse(ret_info):
    """
    输出响应信息，默认为JSON格式
    :param ret_info: dict
    :return: String
    """
    if 'json' == RESPONSE_TYPE:
        return json.dumps(ret_info)
    else:
        return json.dump(ret_info)