# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-6-9'

import smtplib
from email.mime.text import MIMEText

from config import DEBUG_MODE, SMTP_HOST, SMTP_PORT, MAIL_USER, MAIL_PWD, MAIL_SENDER
from models import db_session
from models.trunck import EmailLog

class MailBase:
    def __init__(self, smtp_host, smtp_port, smtp_user, smtp_pwd):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pwd = smtp_pwd
        self.sender = MAIL_SENDER
        self.subject = ''
        self.content = ''
        self.mailto_list = []

    def setSubject(self, subject):
        """
        设置邮件主题
        :param subject:
        :return:
        """
        self.subject = subject

    def setContent(self, content):
        """
        设置邮件内容
        :param content:
        :return:
        """
        self.content = content

    def setMailtoList(self, mailto_list):
        """
        设置邮件接收者
        :param mailto_list:
        :return:
        """
        self.mailto_list = mailto_list

    def send(self):
        raise NotImplementedError



class SMTPMailSender(MailBase):
    def send(self):
        """
        发送邮件
        :return:
        """
        ret_oper = False
        recvers = ";".join(self.mailto_list)
        try:
            smtp_server = smtplib.SMTP()
            smtp_server.connect(self.smtp_host, self.smtp_port)
            smtp_server.login(self.smtp_user, self.smtp_pwd)
            msg = MIMEText(self.content, "html", "utf-8")
            msg['Subject'] = self.subject
            msg['From'] = MAIL_SENDER
            msg['To'] = recvers
            smtp_server.sendmail(self.sender, recvers, msg.as_string())
            ret_oper = True
        except Exception as e:
            pass
        finally:
            try:
                mail_log = EmailLog()
                mail_log.recver = ";".join(self.mailto_list)
                mail_log.subject = self.subject
                mail_log.content = self.content
                mail_log.status = EmailLog.STATUS_SEND_SUCCESS if ret_oper else EmailLog.STATUS_SEND_FAILURE
                db_session.add(mail_log)
                db_session.commit()
            except Exception as e:
                db_session.rollback()
            smtp_server.quit()

        return ret_oper


class SaeMailSender(MailBase):
    """
    使用SAE的邮件接口发送邮件
    """
    def send(self):
        from sae.mail import EmailMessage

        m = EmailMessage()
        m.to = self.mailto_list[0]
        m.subject = self.subject
        m.html = self.content
        m.smtp = (self.smtp_host, 25, self.smtp_user, self.smtp_pwd, False)
        m.send()
        return True

def getMailSender():
    """
    获取一个邮件发送对象
    :param smtp_host:
    :param smtp_port:
    :param smtp_user:
    :param smtp_pwd:
    :return:
    """
    return SMTPMailSender(SMTP_HOST, SMTP_PORT, MAIL_USER, MAIL_PWD)