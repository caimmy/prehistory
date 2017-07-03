# _*_ coding:utf-8 _*_

"""
__project__ : prehistory
__author__  : caimiao
__year__    : 2017
__date__    : 17-6-22
__time__    : 下午10:31

__description__:

"""

from flask import render_template
from admin import admin_app


@admin_app.route("/", methods=["GET"])
def AdminIndex():
    return render_template("index.html")

@admin_app.route("/article_edit", methods=["GET"])
def ArticleNew():
    return "asdf"