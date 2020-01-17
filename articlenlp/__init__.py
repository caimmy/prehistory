# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： __init__.py
@Description:
@Author: caimmy
@date： 2020/1/17 9:53
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""

from flask import Blueprint, request, render_template, current_app, g
from utils.http_helper import JointResponseParams, BaseOperations
from models.trunck import OpsKnowledgeDiscovery

nlp_app = Blueprint("articlenlp", __name__, template_folder="templates")

@nlp_app.route("/", methods=["GET", "POST"])
def IndexAction():
    if "GET" == request.method:
        return render_template("nlp/_index.html", **JointResponseParams())

@nlp_app.route("/word2vec", methods=["GET", "POST"])
def Word2vecIndexAction():
    if "GET" == request.method:
        return render_template("nlp/_word2vec_index.html", **JointResponseParams(books= current_app.word2vecmodel.keys()))
    elif "POST" == request.method:
        httpOperation = BaseOperations()
        posword, negword, book = httpOperation.postParams("posword", "negword", "book")
        if book in current_app.word2vecmodel:
            query_pos = [p.strip() for p in posword.split(" ") if p.strip() != ""]
            query_neg = [n.strip() for n in negword.split(" ") if n.strip() != ""]
            query_pos = query_pos if len(query_pos) > 0 else None
            query_neg = query_neg if len(query_neg) > 0 else None
            relwords = current_app.word2vecmodel[book].most_similar(query_pos, query_neg, topn=100)
        return render_template("nlp/_word2vec_index.html", **JointResponseParams(books= current_app.word2vecmodel.keys(),
                                                                                 relwords=relwords,
                                                                                 curpos=posword,
                                                                                 curneg=negword,
                                                                                 curbook=book))

@nlp_app.route("/kgbackend", methods=["GET", "POST"])
def KnowledgegraphBackendAction():
    if "GET" == request.method:
        res = g.db.query(OpsKnowledgeDiscovery).filter(OpsKnowledgeDiscovery.flag=='0').limit(20)
        return render_template("nlp/_kg_index.html", **JointResponseParams())