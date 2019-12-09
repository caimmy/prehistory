# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-12-6'

import requests
import json
from config import KEY_BAIDU_MAP
from prehistory_conf import MAP_TYPE_GPS_DMS, MAP_TYPE_GPS_DDD, MAP_TYPE_BAIDU_5

QUERY_PAGE_SIZE = 100

#GPS 坐标系编号
SYS_GPS_ID = 1
#百度 坐标系编号
SYS_BAIDU_ID = 5

url_conv_gps2baidu_geo = 'http://api.map.baidu.com/geoconv/v1/?from=%d&to=%d&ak=%s&coords=' % (SYS_GPS_ID, SYS_BAIDU_ID, KEY_BAIDU_MAP)
url_conv_baidu2gps_geo = 'http://api.map.baidu.com/geoconv/v1/?from=%d&to=%d&ak=%s&coords=' % (SYS_BAIDU_ID, SYS_GPS_ID, KEY_BAIDU_MAP)


class BaiduMapApi:

    def geoconv(self, pt_list, gps2baidu, map_type):
        '''
        坐标地址转换
        :return: []
        '''
        i_pt_count = len(pt_list)
        if (0 == (i_pt_count % QUERY_PAGE_SIZE)):
            pages = i_pt_count // QUERY_PAGE_SIZE
        else:
            pages = i_pt_count // QUERY_PAGE_SIZE + 1

        for cur_page_no in range(pages):
            i_start = cur_page_no * QUERY_PAGE_SIZE
            if (i_pt_count > i_start + QUERY_PAGE_SIZE):
                i_end = i_start + QUERY_PAGE_SIZE
            else:
                i_end = i_pt_count
            # 构造百度地址转换接口的批量请求数据
            raw_data = []
            for i_q in range(i_start, i_end):
                raw_data.append("%s,%s" % (self.label2geonumber(pt_list[i_q]['longitude']) if MAP_TYPE_GPS_DMS == map_type else pt_list[i_q]['longitude'],
                                           self.label2geonumber(pt_list[i_q]['latitude']) if MAP_TYPE_GPS_DMS == map_type else pt_list[i_q]['latitude']))
            cor_query = ";".join(raw_data)
            if gps2baidu:
                query_addr = url_conv_gps2baidu_geo + cor_query
            else:
                query_addr = url_conv_baidu2gps_geo + cor_query
            conv_response = requests.get(query_addr)
            if conv_response.ok:
                conv_result = json.loads(conv_response.text)
                if 0 == conv_result['status']:
                    for i_t in range(i_start, i_end):
                        pt_list[i_t].setdefault('bm_longitude', str(conv_result['result'][i_t]['x']))
                        pt_list[i_t].setdefault('bm_latitude', str(conv_result['result'][i_t]['y']))

        return pt_list

    def label2geonumber(self, l):
        '''
        从坐标（度分秒）转换为数值
        :param l:
        :return:
        '''
        d = f = m = None
        dict_chk = l.split("度")
        if 2 == len(dict_chk):
            d = int(dict_chk[0])
        dict_chk = dict_chk[1].split("分")
        if 2 == len(dict_chk):
            f = int(dict_chk[0])
        dict_chk = dict_chk[1].split("秒")
        if 2 == len(dict_chk):
            m = int(dict_chk[0])
        if None in [d,f,m]:
            raise ValueError("坐标转换失败，存在错误的坐标定义！")
        return d + f / 60.0 + m / 3600.0
