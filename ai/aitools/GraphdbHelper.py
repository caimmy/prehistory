# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： GraphdbHelper
@Description:
@Author: caimmy
@date： 2020/1/19 17:14
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""

from py2neo import Graph, Node, Relationship, RelationshipMatcher
from utils.decorates import Singleton
from config import _NEO4J_HOST, _NEO4J_PASS


HISTORY_NODE_LABEL = 'history'

@Singleton
class Neo4jHandler():
    def __init__(self):
        self.neo4j_graph = Graph(_NEO4J_HOST, password=_NEO4J_PASS)


    def MergeEntity(self, name, **kwargs):
        """
        创建实体
        :param name:
        :param kwargs:
        :return:
        """
        _prop = {'name': name}
        _prop.update(kwargs)
        _node = Node(HISTORY_NODE_LABEL, _prop)
        self.neo4j_graph.merge(_node, HISTORY_NODE_LABEL, "name")

    def MakeRelationship(self, sentity, rel, eentity):
        """
        建立实体和关系
        :param sentity:
        :param rel:
        :param eentity:
        :return:
        """
        res = False
        try:
            tx = self.neo4j_graph.begin()
            _s = Node(HISTORY_NODE_LABEL, name=sentity)
            tx.merge(_s, HISTORY_NODE_LABEL, "name")
            _e = Node(HISTORY_NODE_LABEL, name=eentity)
            tx.merge(_e, HISTORY_NODE_LABEL, "name")
            RELS = Relationship.type(rel)
            tx.merge(RELS(_s, _e), rel, "name")
            tx.commit()
            res = True
        except Exception as e:
            print(e)
            res = False
        return res

    def findRelationships(self, nodename):
        """
        查找知识图谱的关系
        :param nodename:
        :return:
        """
        return self.neo4j_graph.run(
            f"MATCH (f:{HISTORY_NODE_LABEL})-[r]-(t) WHERE f.name='{nodename}' return f, r, t"
        ).to_data_frame()
