# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-6-13'

"""
和用户信息相关的功能函数
"""

from flask import request, render_template
from utils.http_helper import BaseOperations
from models import db_session
from models.trunck import User
from utils.mail_helper import getMailSender
from utils.security_helper import UserIdentify

class UserinfoOperations(BaseOperations):
    def handleRegister(self):
        """
        处理用户注册
        :return:
        """
        name, email, pwd = self.postParams('name', 'email', 'pwd')
        if self.checkParamsAvailable(email, pwd):
            """
            exists_query = db_session.query(User).filter(User.email==email).exists()
            if not db_session.query(exists_query).scalar():
                try:
                    set_user = User()
                    set_user.name = name
                    set_user.email = email
                    set_user.salt = User.genSalt()
                    set_user.pwd = User.genPassword(pwd, set_user.salt)
                    set_user.reg_ip = str(request.remote_addr)
                    db_session.add(set_user)
                    db_session.commit()
                    self.changeResponse2Success()
                    mailer = getMailSender()
                    mailer.setMailtoList([email])
                    mailer.setSubject("感谢注册 [史前-在线定量研究工具]")
                    _mail_content = render_template("noticer/email/_register.html", nickname=name)
                    mailer.setContent(_mail_content)
                    mailer.send()
                except Exception as e:
                    db_session.rollback()
                    self.setFailureReason(str(e))
            else:
                self.setFailureReason("该邮箱已经被注册，请更换邮箱申请或尝试找回密码！")
            """
            self.setFailureReason("该邮箱已经被注册，请更换邮箱申请或尝试找回密码！")

    def handleLogin(self):
        """
        处理用户登录
        :return:
        """
        email, pwd = self.postParams('email', 'pwd')
        if self.checkParamsAvailable(email, pwd):
            user_info = db_session.query(User).filter(User.email==email).first()
            if user_info is not None:
                if user_info.checkTOTP(pwd):
                    user_identify = UserIdentify()
                    user_identify.user_login(user_info.id, user_info.email, user_info.name)
                    if not user_identify.is_Guest():
                        self.changeResponse2Success()
                else:
                    self.setFailureReason('密码校验失败！')
            else:
                self.setFailureReason('该邮箱尚未注册，请先注册后再登录系统！')

    def handleLogout(self):
        """
        处理用户注销登录动作
        :return:
        """
        user_info = UserIdentify()
        user_info.user_logout()
        self.changeResponse2Success()


