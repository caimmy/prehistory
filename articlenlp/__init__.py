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
import math
import json
from flask import Blueprint, request, render_template, current_app, g, session
from utils.http_helper import JointResponseParams, BaseOperations
from utils.datatransform import neo4j_data_2_echarts
from models.trunck import OpsKnowledgeDiscovery
from ai.aitools.GraphdbHelper import Neo4jHandler

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
        err_tips = None
        relwords = None
        if book in current_app.word2vecmodel:
            query_pos = [p.strip() for p in posword.split(" ") if p.strip() != ""]
            query_neg = [n.strip() for n in negword.split(" ") if n.strip() != ""]
            query_pos = query_pos if len(query_pos) > 0 else None
            query_neg = query_neg if len(query_neg) > 0 else None
            try:
                relwords = current_app.word2vecmodel[book].most_similar(query_pos, query_neg, topn=100)
            except KeyError as e:
                err_tips = "查询词超出词汇表范围！"
            except Exception as e:
                err_tips = str(e)
        return render_template("nlp/_word2vec_index.html", **JointResponseParams(books= current_app.word2vecmodel.keys(),
                                                                                 relwords=relwords,
                                                                                 curpos=posword,
                                                                                 curneg=negword,
                                                                                 curbook=book,
                                                                                 err_tips=err_tips))

@nlp_app.route("/kgindex", methods=["GET"])
def KnowledgegraphIndexAction():
    operation = BaseOperations()
    if "GET" == request.method:
        word, = operation.getParams("word")
        if word:
            relMatchs = Neo4jHandler().findRelationships(word)
            (nodes, rels) = neo4j_data_2_echarts(relMatchs)

        return render_template("nlp/_kn_graph.html", **JointResponseParams(word=word))

@nlp_app.route("/kgdata", methods=["GET", "POST"])
def KnowledgegraphDataAction():
    operation = BaseOperations()
    if "GET" == request.method:
        session['kgnodes'] = []
        word, = operation.getParams("word")
        ret_data = {
                "results": [
                    {
                        "data": [
                            {"graph": {
                                "nodes": [],
                                "relationships": []
                            }}
                        ]
                    }
                ],
                "errors": []
            }
        if word:
            relMatchs = Neo4jHandler().findRelationships(word)
            (nodes, rels) = neo4j_data_2_echarts(relMatchs)
            session['kgnodes'] = [_n.get("id") for _n in nodes]
            ret_data = {
                "results": [
                    {
                        "data": [
                            {"graph": {
                                "nodes": nodes,
                                "relationships": rels
                            }}
                        ]
                    }
                ],
                "errors": []
            }
        return json.dumps(ret_data)

    elif "POST" == request.method:
        word, = operation.postParams("word")
        ret_data = {
            "nodes": [],
            "relationships": []
        }
        if word:
            relMatchs = Neo4jHandler().findRelationships(word)
            (nodes, rels) = neo4j_data_2_echarts(relMatchs, [])
            session['kgnodes'].extend([_n.get("id") for _n in nodes])
            ret_data = {
                "nodes": nodes,
                "relationships": rels
            }
        return json.dumps(ret_data)


@nlp_app.route("/kgbackend", methods=["GET", "POST", "DELETE"])
def KnowledgegraphBackendAction():
    operation = BaseOperations()
    if "GET" == request.method:
        PAGE_SIZE =  50
        page, = operation.getParams("page")
        try:
            page = int(page)
            if page < 1:
                page = 1
        except Exception as e:
            print(e)
            page = 1
        startpos = (page - 1) * PAGE_SIZE
        query_sql = g.db.query(OpsKnowledgeDiscovery).filter(OpsKnowledgeDiscovery.flag=='0')
        totalpage = math.ceil(query_sql.count() / PAGE_SIZE)
        result_sets = query_sql.offset(startpos).limit(PAGE_SIZE)
        return render_template("nlp/_kg_index.html",
                               **JointResponseParams(totalpage=totalpage, curpage=page, results=result_sets))


    elif "POST" == request.method:
        sentity, rel, eentity = operation.postParams("sentity", "rel", "eentity")
        if all((sentity, rel, eentity)):
            if Neo4jHandler().MakeRelationship(sentity, rel, eentity):
                operation.changeResponse2Success()
        return operation.JsonResponse()

    elif "DELETE" == request.method:
        id, = operation.postParams("id")
        sel_item = g.db.query(OpsKnowledgeDiscovery).filter(OpsKnowledgeDiscovery.id==id).first()
        if sel_item:
            try:
                sel_item.flag = '1'
                g.db.commit()
                operation.changeResponse2Success()
            except Exception as e:
                print(e)
                operation.setFailureReason(str(e))
        return operation.JsonResponse()