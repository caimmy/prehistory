# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-6-7'


from flask import session

def is_Guest():
    """
    用户是否是匿名者
    :return:
    """
    uid = session.get('uid', None)
    return uid is None

class UserIdentify:
    """
    用户标识类
    """
    def __init__(self):
        self.uid = session.get('uid', None)
        self.email = session.get('email', None)
        self.nickname = session.get('nickname', None)

    def user_login(self, uid, email, nickname):
        """
        用户登录
        :param uid:
        :param email:
        :param nickname:
        :return:
        """
        ret_check = False
        try:
            session['uid'] = uid
            session['email'] = email
            session['nickname'] = nickname
            self.uid = uid
            ret_check = True
        except Exception as e:
            pass
        return ret_check

    def user_logout(self):
        """
        用户注销
        :return:
        """
        ret_check = False
        try:
            session.pop('uid', None)
            session.pop('email', None)
            session.pop('nickname', None)
            self.uid = None
            ret_check = True
        except Exception as e:
            pass
        return ret_check

    def is_Guest(self):
        """
        用户是否是匿名者
        :return:
        """
        return self.uid is None

    def current_user(self):
        """
        获取当前用户信息
        :return:
        """
        b_is_guest = self.is_Guest()
        _current_user = {
            'is_guest': b_is_guest,
            'uid': None,
            'email': None,
            'nickname': None
        }
        if not b_is_guest:
            _current_user['uid'] = session['uid']
            _current_user['email'] = session['email']
            _current_user['nickname'] = session['nickname']
        return _current_user

    @staticmethod
    def getCurrentUser():
        user = UserIdentify()
        return user.current_user()