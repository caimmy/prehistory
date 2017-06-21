# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-6-14'

from flask import url_for
from utils import BaseOperations
from models import db_session
from models.trunck import GeoPointGroup, GeoPointUnit
from utils.security_helper import UserIdentify
from prehistory_conf import MAP_TYPE_GPS_DMS, MAP_TYPE_GPS_DDD, MAP_TYPE_BAIDU_5

class ArchgisOperation(BaseOperations):
    def handleScatteredViewpoint(self):
        name, longtitude, latitude, view_pt_list = self.postParams("name", "longitude", "latitude", "view_point_list")

        def _parsePreViewpoints(_view_points):
            _pre_list = []
            _node_list = _view_points.split(";")
            for _node in _node_list:
                _attrs = _node.split("|")
                if 3 == len(_attrs):
                    _pre_list.append({
                        'name': _attrs[0],
                        'longitude': _attrs[1],
                        'latitude': _attrs[2]
                    })
            return _pre_list

        if self.checkParamsAvailable(name, longtitude, latitude):
            pre_view_points = _parsePreViewpoints(view_pt_list)
            pre_view_points.append({
                'name': name,
                'longitude': longtitude,
                'latitude': latitude
            })
            self.setData({'view_points': pre_view_points,
                          'vp_list': "%s;%s" % (view_pt_list, "|".join((name, longtitude, latitude)))})
            self.changeResponse2Success()
        else:
            self.setParamsLostFailure()


    def handleAddGeopointGroup(self):
        """
        创建地理位置集合
        :return:
        """
        name, desc = self.postParams("name", "desc")
        current_user = UserIdentify()
        if self.checkParamsAvailable(name, desc):
            exists_query = db_session.query(GeoPointGroup).filter(GeoPointGroup.name==name).exists()
            if not db_session.query(exists_query).scalar():
                try:
                    geo_group = GeoPointGroup()
                    geo_group.name = name
                    geo_group.desc = desc
                    geo_group.u_id = current_user.uid
                    db_session.add(geo_group)
                    self.changeResponse2Success()
                except Exception as e:
                    self.setFailureReason(str(e))
            else:
                self.setFailureReason("命名冲突，同名记录已经存在！")
        else:
            self.setParamsLostFailure()

    def handleQueryGeoPointInfo(self):
        """
        查询坐标点的模型信息
        :return:
        """
        pid, = self.getParams("pid")
        if self.checkParamsAvailable(pid):
            geo_pt = db_session.query(GeoPointUnit).filter(GeoPointUnit.id==pid).first()
            if geo_pt is not None:
                self.setData(geo_pt.toDict())
                self.changeResponse2Success()
            else:
                self.setFailureReason("坐标未找到！")
        else:
            self.setFailureReason("坐标点主键参数pid未传递！")


    def handleRemoveGeopointGroup(self):
        """
        删除指定的整个地理坐标集合
        需要校验地理坐标集合是否属于操作者本人
        :return:
        """
        gid, pwd = self.postParams("gid", "pwd")
        if self.checkParamsAvailable(gid, pwd):
            if self.userIdentification(pwd):
                current_user = UserIdentify()
                geo_group_info = db_session.query(GeoPointGroup).filter(GeoPointGroup.id==gid).first()
                if geo_group_info is not None:
                    if (geo_group_info.u_id == current_user.uid):
                        try:
                            # 删除集合下的所有观察子节点
                            db_session.query(GeoPointUnit).filter(GeoPointUnit.group_id==gid).delete()
                            db_session.delete(geo_group_info)
                            db_session.commit()
                            self.changeResponse2Success()
                        except Exception as e:
                            self.setFailureReason(str(e), redirect_url=url_for(".ViewGeoGroup", gid=gid))
                    else:
                        self.setFailureReason("该地理坐标点位集合不属于您，无法执行删除操作！", redirect_url=url_for(".ViewGeoGroup", gid=gid))
                else:
                    self.setFailureReason("指定的地理坐标点位集合不存在！", redirect_url=url_for(".ViewGeoGroup", gid=gid))
            else:
                self.setFailureReason("对不起，您不具备执行当前操作的权限！", redirect_url=url_for(".ViewGeoGroup", gid=gid))

    def handleQueryGeoPointUnits(self):
        """
        查询制定地理坐标集合下的所有兴趣点信息
        :return:
        """
        gid, = self.getParams("gid")
        if self.checkParamsAvailable(gid):
            geo_points_collection = {
                MAP_TYPE_GPS_DMS: self._queryGeoPointsOfMaptype(gid, MAP_TYPE_GPS_DMS),
                MAP_TYPE_GPS_DDD: self._queryGeoPointsOfMaptype(gid, MAP_TYPE_GPS_DDD),
                MAP_TYPE_BAIDU_5: self._queryGeoPointsOfMaptype(gid, MAP_TYPE_BAIDU_5)
            }

            self.changeResponse2Success()
            self.setData(geo_points_collection)

    def _queryGeoPointsOfMaptype(self, gid, map_typ):
        """
        获取百度5地图坐标系的数据
        :param gid:
        :return:
        """
        geo_pts = []
        geo_query_res = db_session.query(GeoPointUnit)\
                .filter(GeoPointUnit.group_id==gid)\
                .filter(GeoPointUnit.map_type==map_typ).all()
        for _pt_item in geo_query_res:
            geo_pts.append(_pt_item.toDict())
        return geo_pts

    def handleQueryGeoPointGroups(self):
        """
        查询所有的地理坐标集合记录
        :return:
        """
        current_user = UserIdentify()
        return db_session.query(GeoPointGroup).filter(GeoPointGroup.u_id==current_user.uid).all()

    def handleVeiwQueryGeoPointGroup(self):
        """
        查询地理坐标集合
        :return:
        """
        gid,  = self.getParams("gid")
        if self.checkParamsAvailable(gid):
            geo_point_group = db_session.query(GeoPointGroup).filter(GeoPointGroup.id==gid).first()
            if geo_point_group is not None:
                geo_point_units = db_session.query(GeoPointUnit).filter(GeoPointUnit.group_id==gid).all()
                self.setData({
                    'gid': gid,
                    'geo_point_group': geo_point_group,
                    'geo_point_units': geo_point_units
                })
                self.changeResponse2Success()
            else:
                self.setFailureReason("要查找的地理点位集合不存在！")

    def handleUpdateGeoUnit(self):
        """
        处理地理坐标信息的更新操作
        :return:
        """
        gid, pid, geo_name, longitude, latitude, desc, area, high, map_type = \
            self.postParams("gid", "pid", "geo_name", "longitude", "latitude", "desc", "area", "high", "map_type")
        if self.checkParamsAvailable(gid, pid, geo_name, longitude, latitude, desc, area, high, map_type):
            try:
                current_user = UserIdentify.getCurrentUser()
                geo_unit = db_session.query(GeoPointUnit).filter(GeoPointUnit.id==pid).first()
                geo_unit.name = geo_name
                geo_unit.longitude = longitude
                geo_unit.latitude = latitude
                geo_unit.desc = desc
                geo_unit.map_type = map_type
                if str(high).isdigit():
                    geo_unit.high = high
                else:
                    geo_unit.high = 0
                if str(area).isdigit():
                    geo_unit.area = area
                else:
                    geo_unit.area = 0
                geo_unit.u_id = current_user.get('uid', 0)
                db_session.add(geo_unit)
                db_session.commit()
                self.changeResponse2Success()
            except Exception as e:
                db_session.rollback()
                self.setFailureReason(str(e))


    def handleAddGeoUnit(self):
        """
        处理往地理坐标集合上添加坐标点的工作
        :return:
        """
        gid, geo_name, longitude, latitude, desc, area, high, map_type = \
            self.postParams("gid", "geo_name", "longitude", "latitude", "desc", "area", "high", "map_type")
        if self.checkParamsAvailable(gid, geo_name, longitude, latitude, desc, area, high, map_type):
            try:
                current_user = UserIdentify.getCurrentUser()
                geo_unit = GeoPointUnit()
                geo_unit.group_id = gid
                geo_unit.name = geo_name
                geo_unit.longitude = longitude
                geo_unit.latitude = latitude
                geo_unit.desc = desc
                geo_unit.map_type = map_type
                if str(high).isdigit():
                    geo_unit.high = high
                else:
                    geo_unit.high = 0
                if str(area).isdigit():
                    geo_unit.area = area
                else:
                    geo_unit.area = 0
                geo_unit.u_id = current_user.get('uid', 0)
                db_session.add(geo_unit)
                db_session.commit()
                self.changeResponse2Success()
            except Exception as e:
                db_session.rollback()
                self.setFailureReason(str(e))

    def handleDeleteGeoPointUnit(self):
        """
        从坐标节点集中删除一个坐标节点
        :return:
        """
        gid, geopt = self.getParams("gid", "geopt")
        if self.checkParamsAvailable(gid, geopt):
            geo_unit = db_session.query(GeoPointUnit).filter(GeoPointUnit.group_id==gid).\
                filter(GeoPointUnit.id==geopt).first()
            if geo_unit is not None:
                try:
                    db_session.delete(geo_unit)
                    db_session.commit()
                    self.changeResponse2Success()
                except Exception as e:
                    db_session.rollback()
                    self.setFailureReason(str(e))
            else:
                self.setFailureReason("地理兴趣点坐标未找到")