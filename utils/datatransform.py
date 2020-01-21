# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： datatransform
@Description:
@Author: caimmy
@date： 2020/1/21 9:46
-------------------------------------------------
Change Activity:

进行数据转换工作
-------------------------------------------------
"""

import re
import pandas as pd

KG_REL_REGEX = re.compile("^\((\w+)\)-\[:(\w+)\s\{\}\]->\((\w+)\)$")

def neo4j_data_2_echarts(df: pd.DataFrame, exclude_nodes: list = []) -> (list, list):
    """
    将 neo4j 查询得到的面板数据转换成图表所需的数据
    :param df:
    :return:
    """
    _node_list = set()
    _rel_list = list()

    _shape = df.shape
    for i in range(_shape[0]):
        _node_list.add(df.iloc[i].f.get("name"))
        _node_list.add(df.iloc[i].t.get("name"))
        _rel_tuple = KG_REL_REGEX.findall(str(df.iloc[i].r))
        _rel_list.extend(_rel_tuple)

    neo_nodes = []
    neo_rels = []
    for _n in _node_list:
        if not _n in exclude_nodes:
            neo_nodes.append({
                'id': _n,
                'labels': [_n],
                'properties': {}
            })
    _rseq = 1
    for _r in _rel_list:
        if not (_r[0] in exclude_nodes and _r[2] in exclude_nodes):
            neo_rels.append({
                "id": _rseq,
                "type": _r[1],
                "startNode": _r[0],
                "endNode": _r[2],
                "properties": {}
            })
            _rseq += 1
    return (neo_nodes, neo_rels)
