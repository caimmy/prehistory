# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-5-5'

from flask import Blueprint

admin_app = Blueprint("admin", __name__, template_folder="templates")