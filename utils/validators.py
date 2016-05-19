# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-6-7'

SUCCESS_RESPONSE_CODE = 0

def checkExistsNone(*args, **kwargs):
    """
    检查传入参数中是否有空值
    :param args:
    :param kwargs:
    :return:
    """
    ret_check = False
    for _arg in args:
        if _arg is None:
            ret_check = True
            break
    return ret_check

def genFailureResponse():
    """
    生成失败的响应
    :return:
    """
    return {
        'code': -1,
        'msg': 'failure',
        'success': False,
        'redirect_url': '#'     # 失败时的重定向地址
    }

def genSuccessResponse():
    """
    生成成功的响应
    :return:
    """
    return {
        'code': SUCCESS_RESPONSE_CODE,
        'msg': 'success',
        'success': True
    }

def setFailureReason(response, msg, code=-1):
    """
    设置失败的响应信息
    :param msg:
    :param code:
    :return:
    """
    response['code'] = code
    response['msg'] = msg
    return response


def changeResponse2Success(response):
    """
    转换失败的响应为成功
    :param response:
    :return:
    """
    response['code'] = SUCCESS_RESPONSE_CODE
    response['msg'] = 'success'
    response['success'] = True
    return response

def checkResponseSuccessful(response):
    """
    检查响应信息是否成功
    :param response:
    :return: bool
    """
    ret_info = False
    if isinstance(response, dict) and response.get('success', False):
        return True
    else:
        return False