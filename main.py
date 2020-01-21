# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-3-30'


import base64

from flask import Flask, g, render_template, request, redirect, url_for, make_response, current_app

from models import db_session
from models.trunck import AccessLog

from archgis import archgis_app
from archaeology import archaeology_app
from visual import visual_app
from admin import admin_app
from admin.article_entry import *
from articlenlp import nlp_app
from archaeology.userinfo_operation import UserinfoOperations
from utils.url_helper import makeTipsPageUrl
from utils.security_helper import UserIdentify
from utils.encode_helper import ensure_string
from utils.apptools import loadAllWord2vecModels
from config import DEBUG_MODE, ACCESS_LOG_ON


app = Flask(__name__)
app.debug = DEBUG_MODE
app.secret_key = '\xac\xe7\x03f\x04n<\xdc\xb0\x82\xf4\xde\xc8\x7f\xefE\xd4=E`0S\x0f\xed'

app.register_blueprint(archgis_app, url_prefix='/gis')
app.register_blueprint(archaeology_app, url_prefix='/arch')
app.register_blueprint(visual_app, url_prefix='/visual')
app.register_blueprint(admin_app, url_prefix='/admin')
app.register_blueprint(nlp_app, url_prefix='/nlp')
app.word2vecmodel = loadAllWord2vecModels()

@app.route('/')
def frontpage():
    return render_template("welcome.html",
                           current_user=UserIdentify.getCurrentUser(),
                           url_arch_laborary=url_for("archaeology.Index"),
                           url_arch_gis=url_for("archgis.Index"),
                           url_arch_nlp=url_for("articlenlp.IndexAction")
                           )

@app.errorhandler(404)
def test_404(error):
    return '<h1>404 occur</h1><br />%s' % (str(error)), 404


@app.before_request
def before_request():
    g.db = db_session
    if ACCESS_LOG_ON:
        user_identify = UserIdentify()
        try:
            access_log = AccessLog()
            access_log.ip = str(request.remote_addr)
            access_log.path = str(request.path)
            access_log.email = 'anonymous' if user_identify.is_Guest() else user_identify.email
            db_session.add(access_log)
            db_session.commit()
        except Exception as e:
            db_session.rollback()

@app.teardown_request
def tear_down(exception):
    if hasattr(g, "db"):
        g.db.close()
    pass

'''
====================================================
*** 以下函数需要在部署生产环境时删除
====================================================
'''

@app.route("/pagetest")
def Pagetest():
    from io import StringIO
    import numpy as np
    from matplotlib import pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(np.random.randn(50).cumsum(), 'r--')
    buf = StringIO()
    plt.savefig(buf, dpi=50, fmt="png")
    response = make_response(buf.getvalue())
    response.headers['Content-Type'] = 'Image/png'
    #response.headers['Content-Type'] = 'text/html;charset=utf8'
    return response

@app.route("/pagetest2")
def pagetest2():
    import numpy as np
    from matplotlib import pyplot as plt
    from pandas import Series, DataFrame
    import pandas as pd
    from io import StringIO

    df = DataFrame(np.random.rand(6,4), index=["One", "Two", "Three", "Four", "Five", "Six"], columns=pd.Index(["A", "B", "C", "D"], name="Genus"))
    buf = StringIO()
    df.to_pickle(buf)
    response = make_response(buf.getvalue())
    response.headers['Content-Type'] = 'Image/png'
    #response.headers['Content-Type'] = 'text/html;charset=utf8'
    return response

@app.route("/rebuilddb")
def RebuildDatabase():
    from models import mysql_master_engine, Base

    drop_before = request.args.get("dropall", "no")
    if "yes" == drop_before:
        Base.metadata.drop_all(mysql_master_engine)
    Base.metadata.create_all(mysql_master_engine)

    return redirect(makeTipsPageUrl("系统操作", "重建数据库操作执行完成！", "success"))

'''
====================================================
*** 以上函数需要在部署生产环境时删除
====================================================
'''


@app.route("/tips")
def TipsPage():
    _title = request.args.get("title", "")
    _content = request.args.get("content", "")
    _theme = request.args.get("theme", "info")
    _jumpurl = request.args.get('jumpUrl', '')
    return render_template("gen/_tips.html", current_user=UserIdentify.getCurrentUser(),
                           title=ensure_string(base64.b64decode(_title)),
                           content=ensure_string(base64.b64decode(_content)),
                           theme=_theme, jumpUrl=_jumpurl)

@app.route("/register", methods=["GET", "POST"])
def Register():
    if "GET" == request.method:
        return render_template("gen/_register.html", current_user=UserIdentify.getCurrentUser())
    else:
        user_operations = UserinfoOperations()
        user_operations.handleRegister()
        _res, response = user_operations.getResponse()
        _jump_url = makeTipsPageUrl("注册成功", "您的帐号已经成功注册，请返回首页在顶部登录表单登录系统！", "success") if _res \
            else makeTipsPageUrl("注册失败", response['msg'], "danger")
        return redirect(_jump_url)


@app.route("/login", methods=["POST"])
def Login():
    user_operation = UserinfoOperations()
    user_operation.handleLogin()
    _res, response = user_operation.getResponse()
    if _res:
        return redirect(url_for("frontpage"))
    else:
        return redirect(makeTipsPageUrl("登录失败", response['msg'], 'danger'))

@app.route("/logout", methods=["GET"])
def Logout():
    user_operation = UserinfoOperations()
    user_operation.handleLogout()
    return redirect(url_for("frontpage"))

if "__main__" == __name__:
    listen_port = 5000
    print("listen on port %d" % (listen_port))
    app.run(port=listen_port, debug=False)