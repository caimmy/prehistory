# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-5-7'

from models import db_session
from models.trunck import Settlement, GeoPoint

class SettlementMgr:
    def __init__(self):
        pass

    @staticmethod
    def addNewSettlement(name, desc, ref, longitude=0, latitude=0, hl=0, hh=0, area=0):
        """
        添加新的遗址聚落点
        :param name: 聚落名称
        :param desc: 描述
        :param ref: 引文
        :param longitude: 经度
        :param latitude: 纬度
        :param hl: 海拔高点
        :param hh: 海拔低点
        :param area: 探查面积
        :return:
        """
        ins_id = 0
        if name:
            try:
                settlement_pt = Settlement()
                settlement_pt.name = name
                settlement_pt.desc = desc
                settlement_pt.ref = ref
                db_session.add(settlement_pt)
                db_session.flush()
                ins_id = settlement_pt.id

                geo_point = GeoPoint()
                geo_point.belong = ins_id
                geo_point.longitude = longitude
                geo_point.latitude = latitude
                geo_point.height_h = int(hh) if '' != hh else 0
                geo_point.height_l = int(hl) if '' != hl else 0
                geo_point.area = int(area) if '' != area else 0
                db_session.add(geo_point)

                db_session.commit()
            except Exception:
                ins_id = -1
                db_session.rollback()
        return ins_id

    @staticmethod
    def getAllSettlement():
        return db_session.query(Settlement, GeoPoint).filter(Settlement.id==GeoPoint.belong).all()