# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-3-30'

from flask import Blueprint, render_template, redirect, url_for, request
from archgis.archgis_lib import SettlementMgr
from archgis.bd_map_api import BaiduMapApi
from archgis.archgis_operation import ArchgisOperation
from utils.tools import getFailureResponse, changeResponseToSuccess, makeResponse
from utils.security_helper import UserIdentify
from utils.url_helper import makeTipsPageUrl
from utils.decorates import login_required
from config import KEY_BAIDU_MAP
from prehistory_conf import MAP_TYPE_GPS_DMS, MAP_TYPE_GPS_DDD, MAP_TYPE_BAIDU_5

archgis_app = Blueprint('archgis', __name__, template_folder='templates')

@archgis_app.route("/", methods=["GET", "POST"])
def Index():
    if "GET" == request.method:
        return render_template("archgis/_index.html",
                               current_user=UserIdentify.getCurrentUser(),
                               url_geogroup_tbl=url_for(".QueryGeopointGroup"))
    else:
        archgis_operation = ArchgisOperation()
        archgis_operation.handleScatteredViewpoint()
        res, response = archgis_operation.getResponse()
        if res:
            res_data = archgis_operation.getData()
            return render_template("archgis/_index.html", current_user=UserIdentify.getCurrentUser(),
                                   view_points=res_data['view_points'], vp_list=res_data['vp_list'])
        else:
            return archgis_operation.jumpErrorRedirect()

@archgis_app.route("/query_geopoint_group", methods=["GET", "POST"])
def QueryGeopointGroup():
    archgis_operation = ArchgisOperation()
    if "GET" == request.method:
        geo_point_group = archgis_operation.handleQueryGeoPointGroups()
        return render_template("archgis/_geopt_group_table.html",
                               geo_pt_group=geo_point_group,
                               url_view_group_detail=url_for(".ViewGeoGroup"))
    else:
        if not UserIdentify().is_Guest():
            archgis_operation.handleAddGeopointGroup()
            _, response = archgis_operation.getResponse()
        else:
            response = getFailureResponse()
            response['msg'] = '用户需要登录'
        return ArchgisOperation.jsonEncode(response)

@archgis_app.route("/view_geopoint_group", methods=["GET"])
def ViewGeoGroup():
    """
    展示地理坐标集合页面
    :return:
    """
    archgis_operation = ArchgisOperation()
    archgis_operation.handleVeiwQueryGeoPointGroup()
    res, response = archgis_operation.getResponse()
    if res:
        return render_template("archgis/_geopt_group_detail.html",
                               current_user=UserIdentify.getCurrentUser(),
                               gid=response['data']['gid'],
                               geo_point_group=response['data']['geo_point_group'],
                               geo_point_units=response['data']['geo_point_units'],
                               map_gps_dms=MAP_TYPE_GPS_DMS,
                               map_gps_ddd=MAP_TYPE_GPS_DDD,
                               map_baidu_5=MAP_TYPE_BAIDU_5,
                               url_module_index=url_for(".Index"),
                               url_add_geopoint=url_for(".AddGeoUnitOnGroup"),
                               url_del_geopoint=url_for(".DeleteGeoUnit"),
                               url_del_geogrp=url_for(".RemoveGeoGroup"),
                               url_query_geopoint=url_for(".QueryGeoUnitInfo"),
                               url_watch_geogrp=url_for(".WatchGeoGroupInArchGisMap"),
                               url_watch_baidu_geogrp=url_for(".WatchGeoGroupInBaiduMap"))
    else:
        return archgis_operation.jumpErrorRedirect("错误", jumpurl=url_for(".Index"))

@archgis_app.route("/watch_baidugeogrp", methods=["GET", "POST"])
def WatchGeoGroupInBaiduMap():
    """
    在百度地图系统中观察地理点位集合
    :return:
    """
    if "GET" == request.method:
        gid = request.args.get('gid', None)
        if gid is not None and '' != gid:
            archgis_operation = ArchgisOperation()
            archgis_operation.handleQueryGeoPointUnits()
            res, _ = archgis_operation.getResponse()
            query_data = archgis_operation.getData()
            _view_pts_dms = query_data[MAP_TYPE_GPS_DMS] if res else []
            _view_pts_ddd = query_data[MAP_TYPE_GPS_DDD] if res else []
            _view_pts_baidu5 = query_data[MAP_TYPE_BAIDU_5] if res else []
            baidu_map_api = BaiduMapApi()
            # 进行百度坐标系转换
            _conv_view_pts_dms = baidu_map_api.geoconv(_view_pts_dms, True, MAP_TYPE_GPS_DMS)
            _conv_view_pts_ddd = baidu_map_api.geoconv(_view_pts_ddd, True, MAP_TYPE_GPS_DDD)
            return render_template('archgis/_baidumap_view.html',
                                   gid=gid,
                                   current_user=UserIdentify.getCurrentUser(),
                                   key=KEY_BAIDU_MAP,
                                   view_pts_dms=_conv_view_pts_dms,
                                   view_pts_ddd=_conv_view_pts_ddd,
                                   view_pts_baidu5=_view_pts_baidu5)

@archgis_app.route("/watch_geogrp", methods=["GET", "POST"])
def WatchGeoGroupInArchGisMap():
    """
    在ArchGis地图中观察地理点位集合
    :return:
    """
    if "GET" == request.method:
        gid=request.args.get('gid', None)
        if gid is not None and '' != gid:
            archgis_operation = ArchgisOperation()
            archgis_operation.handleQueryGeoPointUnits()
            res, _ = archgis_operation.getResponse()
            query_data = archgis_operation.getData()
            _view_pts_dms = query_data[MAP_TYPE_GPS_DMS] if res else []
            _view_pts_ddd = query_data[MAP_TYPE_GPS_DDD] if res else []
            baidu_map_api = BaiduMapApi()
            _view_pts_baidu5 = query_data[MAP_TYPE_BAIDU_5] if res else []
            _conv_pts_baidu5 = baidu_map_api.geoconv(_view_pts_baidu5, False, MAP_TYPE_BAIDU_5)
            return render_template("archgis/_mapview.html",
                                   gid=gid,
                                   current_user=UserIdentify.getCurrentUser(),
                                   view_pts_dms=_view_pts_dms,
                                   view_pts_ddd=_view_pts_ddd,
                                   view_pts_baidu5=_conv_pts_baidu5)
        else:
            return redirect(makeTipsPageUrl("错误", "您要观察的坐标集合不存在", "danger", url_for(".Index")))
    else:
        archgis_operation = ArchgisOperation()
        archgis_operation.handleQueryGeoPointUnits()
        res, response = archgis_operation.getResponse()
        return archgis_operation.jsonEncode(response)

@archgis_app.route("/remove_geogrp", methods=["POST"])
@login_required
def RemoveGeoGroup():
    """
    删除地理坐标集合
    AJAX+JSON
    :return:
    """
    archgis_operation = ArchgisOperation()
    archgis_operation.handleRemoveGeopointGroup()
    res, response = archgis_operation.getResponse()
    return archgis_operation.jsonEncode(response)

@archgis_app.route("/add_geo_unit_on_group", methods=["POST"])
@login_required
def AddGeoUnitOnGroup():
    """
    在地理坐标集合上增加一个兴趣坐标点
    :return:
    """
    archgis_operation = ArchgisOperation()
    oper, gid, geo_name, longitude, latitude, desc, area, high, map_type = \
        archgis_operation.postParams("oper", "gid", "geo_name", "longitude", "latitude", "desc", "area", "high", "map_type")
    if archgis_operation.checkParamsAvailable(oper, gid, geo_name, longitude, latitude, area, high, map_type):
        if "create" == oper:
            archgis_operation.handleAddGeoUnit()
        elif "update" == oper:
            archgis_operation.handleUpdateGeoUnit()
        res, response = archgis_operation.getResponse()
        if res:
            return redirect(url_for(".ViewGeoGroup", gid=gid))
        else:
            return archgis_operation.jumpErrorRedirect("添加坐标失败", url_for(".ViewGeoGroup", gid=gid))

@archgis_app.route("/query_geo_pt_unit")
@login_required
def QueryGeoUnitInfo():
    """
    查询一个坐标点的信息
    :return:
    """
    archgis_operation = ArchgisOperation()
    archgis_operation.handleQueryGeoPointInfo()
    res, response = archgis_operation.getResponse()
    return makeResponse(response)


@archgis_app.route("/delete_geopt")
@login_required
def DeleteGeoUnit():
    """
    在地理坐标集合上删除一个兴趣坐标点
    :return:
    """
    archgis_operation = ArchgisOperation()
    gid, = archgis_operation.getParams("gid")
    archgis_operation.handleDeleteGeoPointUnit()
    res, response = archgis_operation.getResponse()
    if res:
        return redirect(url_for(".ViewGeoGroup", gid=gid))
    else:
        return archgis_operation.jumpErrorRedirect("删除坐标失败", url_for(".ViewGeoGroup", gid=gid))

@archgis_app.route('/mapview', methods=['GET'])
def Mapview():
    return render_template('archgis/_mapview.html', query_url=url_for(".ajax_get_settlements"))

@archgis_app.route('/load_settles', methods=['POST'])
@login_required
def ajax_get_settlements():
    ret_info = getFailureResponse()
    settlement_list = SettlementMgr.getAllSettlement()
    settle_pts = []
    for _p in settlement_list:
        settle_pts.append({'name': _p[0].name, 'long': _p[1].longitude, 'lati': _p[1].latitude,
                           'desc': _p[0].desc})
    changeResponseToSuccess(ret_info)
    ret_info['data'] = settle_pts
    return makeResponse(ret_info)

@archgis_app.route('/edit', methods=['GET'])
def GetEdit():
    settlement_list = SettlementMgr.getAllSettlement()
    settle_pts = []
    for _p in settlement_list:
        settle_pts.append({'name': _p[0].name, 'long': _p[1].longitude, 'lati': _p[1].latitude,
                           'desc': _p[0].desc})
    return render_template('archgis/_edit.html', form_url=url_for('.AddSettlement'),
                           settlements=settle_pts)

@archgis_app.route('/add_settlement', methods=['POST'])
def AddSettlement():
    form_data = request.form
    ins_id = SettlementMgr.addNewSettlement(form_data.get('settlement_name'), form_data.get('desc'), form_data.get('rel'),
                                            form_data.get('longitude'), form_data.get('latitude'),
                                            form_data.get('height_h'), form_data.get('height_l'), form_data.get('area'))
    return redirect(url_for('.GetEdit'))

@archgis_app.route('/test')
def Test():
    return render_template('archgis/_test.html')