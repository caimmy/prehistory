# _*_ coding:utf-8 _*_
'''
@author: caimmy@qq.com
@license: FREE

@contact: http://www.github.com/caimmy
@software: in ksg

@file: http_helper.py
@time: 17-6-21 下午4:29
@desc:

'''


import json
from flask import request, redirect
from models import db_session
from models.trunck import User
from utils.validators import genFailureResponse, checkResponseSuccessful
from utils.url_helper import makeTipsPageUrl
from utils.security_helper import UserIdentify


class BaseOperations:
    SUCCESS_RESPONSE_CODE = 0

    def __init__(self):
        self.response = genFailureResponse()

    def requestParams(self, *args, **kwargs):
        """
        从GET、POST中获取前端请求参数
        :param args:
        :param kwargs:
        :return:
        """
        params = []
        for _a in args:
            if _a in request.args:
                _t_p = request.args.get(_a, None)
                if isinstance(_t_p, str):
                    params.append(_t_p.strip())
                else:
                    params.append(_t_p)
            elif _a in request.form:
                _t_p = request.form.get(_a, None)
                if isinstance(_t_p, str):
                    params.append(_t_p.strip())
                else:
                    params.append(_t_p)
        return params

    def postParams(self, *args, **kwargs):
        if 1 == len(args) and "*" == args[0]:
            return request.form
        params = []
        for _a in args:
            _t_p = request.form.get(_a, None)
            if isinstance(_t_p, str):
                params.append(_t_p.strip())
            else:
                params.append(_t_p)
        return params

    def getParams(self, *args, **kwargs):
        params = []
        for _a in args:
            _t_p = request.args.get(_a, None)
            if isinstance(_t_p, str):
                params.append(_t_p)
            else:
                params.append(_t_p)
        return params

    def getResponse(self):
        """
        获取请求执行结果
        :return:
        """
        return checkResponseSuccessful(self.response), self.response

    def isSuccess(self):
        """
        判断请求执行是否成功
        :return:
        """
        return checkResponseSuccessful(self.response)

    def checkParamsAvailable(self, *args, **kwargs):
        """
        判断参数中是否全部非空，可用
        :param args:
        :param kwargs:
        :return:
        """
        exists_none = False
        for _p in args:
            if _p is None or "" == args:
                exists_none = True
                break
        if exists_none:
            self.setParamsLostFailure()
        return not exists_none

    def setFailureReason(self, msg, code=-1, redirect_url='#'):
        """
        设置失败的响应信息
        :param msg:
        :param code:
        :return:
        """
        self.response['code'] = code
        self.response['msg'] = msg
        self.response['redirect_url'] = redirect_url
        return self.response

    def setParamsLostFailure(self):
        """
        设置参数丢失的失败响应
        :return:
        """
        return self.setFailureReason('重要参数丢失，请重新执行操作！')

    def changeResponse2Success(self):
        """
        转换失败的响应为成功
        :param response:
        :return:
        """
        self.response['code'] = BaseOperations.SUCCESS_RESPONSE_CODE
        self.response['msg'] = 'success'
        self.response['success'] = True
        return self.response

    def setData(self, _data):
        """
        设置结果信息
        :param _data:
        :return:
        """
        self.response['data'] = _data

    def getMsg(self):
        """
        获取响应消息中的msg字段
        :return:
        """
        return self.response.get("msg", "")

    def getData(self):
        """
        获取响应消息中的data（结果字段）
        :return:
        """
        return self.response.get("data", None)

    def jumpErrorRedirect(self, title=None, jumpurl=''):
        """
        进行错误提示跳转
        :return:
        """
        return redirect(makeTipsPageUrl("错误" if title is None else title, self.getMsg(), 'danger', jumpurl))

    def ajaxErrorInfoTips(self, title=None, msg=None):
        """
        显示错误信息警告框
        :param msg:
        :param title:
        :return:
        """
        return '''<div class="alert alert-danger" role="alert">
                  <strong>%s</strong> %s
                </div>''' % ('错误' if title is None else title, self.getMsg() if msg is None else msg)

    def userIdentification(self, pwd):
        """
        用户的身份判别，检查执行当前操作的用户是否真正拥有该用户的密码
        :param pwd:
        :return: bool
        """

        ret_check = False
        current_user = UserIdentify()
        if not current_user.is_Guest():
            user_info = db_session.query(User).filter(User.id==current_user.uid).first()
            if user_info is not None and user_info.checkPassword(pwd):
                ret_check = True
        return ret_check


    @staticmethod
    def jsonEncode(data=None):
        """
        进行JSON编码
        :param data:
        :return:
        """
        return json.dumps(data)



def JointResponseParams(*args, **kwargs):
    """
    整合输出参数
    :param args: 
    :param kwargs: 
    :return: 
    """
    _dict = {"current_user": UserIdentify.getCurrentUser()}
    _dict.update(kwargs)
    return _dict