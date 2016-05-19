# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-7-3'

from flask import Blueprint, render_template

from utils.decorates import login_required
from utils.security_helper import UserIdentify

visual_app = Blueprint("visual", __name__, template_folder="templates")

@visual_app.route("/liner", methods=["GET"])
@login_required
def ViewLiner():
    return render_template("/visual/_liner.html",
                           current_user=UserIdentify.getCurrentUser())