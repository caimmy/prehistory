# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-5-5'

import hashlib, random, pyotp, time

from sqlalchemy import Column, Integer, String, DateTime, Enum, CHAR, Text
from datetime import datetime
from models import Base, SQLExtHelper, db_session
from utils.encode_helper import ensure_bytes

from prehistory_conf import MAP_TYPE_GPS_DMS


class EmailLog(Base):
    """
    邮件发送日志记录
    """
    __tablename__ = 'arch_email'

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_tm = Column(DateTime, default=datetime.now())
    recver = Column(String(512), default='')
    subject = Column(String(128), default='')
    content = Column(Text)
    status = Column(Enum('0', '1'), default='0')

    STATUS_SEND_FAILURE = '0'
    STATUS_SEND_SUCCESS = '1'

    def __repr__(self):
        return "<<Email> recver: %s, subject: %s, content: %s >" % (self.recver, self.subject, self.content)

class AccessLog(Base):
    """
    系统的访问日志
    """
    __tablename__ = "arch_access_log"

    id = Column(Integer, primary_key=Text, autoincrement=True)
    ip = Column(String(128), default='')
    tm = Column(DateTime, default=datetime.now())

    path = Column(String(256), default='')
    email = Column(String(128), default='')

    def __repr__(self):
        return "<<AccessLog> email: %s, tm: %s, path: %s >" % (self.email, self.tm, self.path)


class User(Base):
    '''
    用户表
    '''
    __tablename__ = 'arch_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    email = Column(String(128), nullable=False)
    pwd = Column(String(32))
    salt = Column(String(32))
    otpkey = Column(String(32))
    reg_ip = Column(String(128), default='')
    reg_tm = Column(DateTime, default=datetime.now())
    avatar = Column(String(256))

    salt_pool = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
                 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
                 'y', 'z', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')']

    @staticmethod
    def genSalt():
        """
        产生密码盐
        :return string
        """
        _salt = ''
        for i in range(0, 8):
            _salt += User.salt_pool[random.randint(0, len(User.salt_pool) - 1)]
        return _salt

    @staticmethod
    def genPassword(pwd, salt):
        """
        生成加盐后的密码
        :param pwd 密码
        :param salt 混淆盐
        :return string
        """
        md5_obj = hashlib.md5()
        md5_obj.update("%s%s" % (pwd, salt))
        return md5_obj.hexdigest()

    def checkTOTP(self, code):
        """
        通过totp校验检查用户是否有权登录系统
        :return bool
        """
        ret_check = False
        if self.otpkey and len(self.otpkey) > 0:
            otpChecker = pyotp.TOTP(self.otpkey)
            now_tm = int(time.time())
            for _chk_code in (now_tm - 30, now_tm, now_tm + 30):
                if otpChecker.verify(code, _chk_code):
                    ret_check = True
                    break
        return ret_check

    def checkPassword(self, chk_pwd):
        """
        检查密码是否正确
        :param chk_pwd 登录时传递的密码
        :return bool
        """
        md5_obj = hashlib.md5()
        md5_obj.update(ensure_bytes("%s%s" % (chk_pwd, self.salt)))
        _check_value = md5_obj.hexdigest()
        return str(_check_value).lower() == str(self.pwd).lower()

    def __repr__(self):
        return "<<Table User> name:%s, email:%s>" % (self.name, self.email)

class Settlement(Base):
    '''
    聚落点
    '''
    __tablename__ = 'arch_settlement'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    desc = Column(Text)
    ref = Column(String(256))                   # 来源
    create_tm = Column(DateTime, default=datetime.now())


class GeoPoint(Base):
    '''
    地理坐标
    '''
    __tablename__ = 'arch_geo_point'

    id = Column(Integer, primary_key=True, autoincrement=True)
    longitude = Column(String(64), nullable=False)
    latitude = Column(String(64), nullable=False)
    height_l = Column(Integer)                          # 高度的低点
    height_h = Column(Integer)                          # 高度的高点
    area = Column(Integer)                              # 面积（平方米）
    belong = Column(Integer, nullable=False)            # 所属聚落点
    create_tm = Column(DateTime, default=datetime.now())


class GeoPointGroup(Base):
    """
    需要观察的地理坐标点的集合
    """
    __tablename__ = "arch_geopoint_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    create_tm = Column(DateTime, default=datetime.now())
    u_id = Column(Integer, index=True)
    desc = Column(Text, default='')

    def __repr__(self):
        return "<<GeoPointGroup> name: %s >" % (self.name)

class GeoPointUnit(Base, SQLExtHelper):
    """
    需要观察的地理坐标点个体
    """
    __tablename__ = 'arch_geopoint_unit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    create_tm = Column(DateTime, default=datetime.now())
    u_id = Column(Integer, index=True)
    group_id = Column(Integer, index=True)              # 地理点所属的组编号
    desc = Column(Text, default='')
    longitude = Column(String(32), nullable=False)      # 地理点位的经度
    latitude = Column(String(32), nullable=False)       # 地理点位的纬度
    high = Column(Integer, default=0)                   # 地理点位的海拔高度
    area = Column(String(20), default='0')              # 地理点的面积
    map_type= Column(Integer, default=MAP_TYPE_GPS_DMS)

    def __repr__(self):
        return "<<GeoPointUnit> name : %s, longitude: %s, latitude: %s, high: %d >" % \
               (self.name, self.longitude, self.latitude, self.high)

class Laborary(Base, SQLExtHelper):
    """
    实验室数据表
    """
    __tablename__ = 'arch_laborary'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), index=True, unique=True)
    desc = Column(Text, default='')
    unit = Column(String(128), default='')  # 所属单位
    u_id = Column(Integer, default=0)
    create_tm = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return "<<Laborary> name: %s, desc: %s>" % (self.name, self.desc)

class Project(Base, SQLExtHelper):
    """
    实验项目
    """
    __tablename__ = 'arch_project'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), index=True)
    desc = Column(Text, default='')
    l_id = Column(Integer, nullable=False, index=True)          # 所属的实验室编号
    create_tm = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return "<<Project> name: %s, desc: %s>" % (self.name, self.desc)


class ProjectProperty(Base):
    """
    实验项目的数据结构
    """
    __tablename__ = 'arch_pproperty'

    TYPE_NAMING = '0'               # 名称变量
    TYPE_SEQUENCE = '1'             # 有序变量
    TYPE_NUMBER = '2'               # 数值变量

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), index=True, unique=True)           # 属性名称
    label = Column(String(64), nullable=False, unique=True)      # 属性标识，参与计算使用
    type = Column(Enum('0', '1', '2'), default='0') # 属性的数据类型，名称、有序、数值
    desc = Column(Text, default='')                 # 属性的描述信息
    p_id = Column(Integer, nullable=False, index=True)          # 所属的实验项目编号
    create_tm = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return "<<ProjectProperty> name: %s, label: %s, type: %s>" % (self.name, self.label, self.type)

    def getTypeLabel(self):
        """
        获取类型字段的定义
        """
        if self.TYPE_NAMING == self.type:
            return '名称变量'
        elif self.TYPE_SEQUENCE == self.type:
            return '有序变量'
        elif self.TYPE_NUMBER == self.type:
            return '数值变量'
        else:
            return self.type

    def typeIsNaming(self):
        """
        字段属性为名称变量
        @return bool
        """
        return self.type == ProjectProperty.TYPE_NAMING

    def typeIsSequence(self):
        """
        字段属性为有序变量
        @return bool
        """
        return self.type == ProjectProperty.TYPE_SEQUENCE

    def typeOptions(self):
        """
        是有序变量或名称变量
        :return:
        """
        return self.typeIsSequence()

    def getPropertyOptions(self):
        """
        如果是有序变量或名称变量，则获取其可取数值列表
        @return list
        """
        if self.typeOptions():
            return db_session.query(PropertyOptions).filter(PropertyOptions.p_id==self.id).all()

class PropertyOptions(Base):
    """
    名称变量及有序变量的选项
    """
    __tablename__ = 'arch_property_option'

    id = Column(Integer, primary_key=True, autoincrement=True)
    p_id = Column(Integer, nullable=False, index=True)      # 所属属性的编号
    name = Column(String(32), nullable=False, unique=True)
    label = Column(String(32), unique=True)
    weight = Column(Integer)            # 选项的权重，属性为有序变量时其作用

    def __repr__(self):
        return "<<PropertyOptions> p_id: %d, name: %s, label: %s >" % (self.p_id, self.name, self.label)

class ProjectItem(Base):
    """
    实验项目的数据记录
    """
    __tablename__ = 'arch_precord'

    id = Column(Integer, primary_key=True, autoincrement=True)
    row_id = Column(String(64), nullable=False)     # 行编号
    label = Column(String(64), nullable=False)
    proj_id = Column(Integer, nullable=False, index=True)       # 所属的实验项目
    p_id = Column(Integer, nullable=False)          # 数据记录的属性
    value = Column(String(64))
    create_tm = Column(DateTime, default=datetime.now())

    def loadValueLabel(self):
        """
        获取有序变量的取值
        :return:
        """
        _lb = self.value
        property_rel = db_session.query(ProjectProperty).filter(ProjectProperty.id==self.p_id).first()
        if property_rel is not None and property_rel.type == ProjectProperty.TYPE_SEQUENCE:
            property_option = db_session.query(PropertyOptions).filter(PropertyOptions.p_id==self.p_id).\
                filter(PropertyOptions.label==self.value).first()
            if property_option is not None:
                _lb = property_option.name

        return _lb


    def __repr__(self):
        return "<<ProjectItem> label: %s, proj_id: %d, p_id: %d, value: %s>" % (self.label, self.proj_id, self.p_id, self.value)


###################################################################
#  人工智能辅助工具表
###################################################################

class OpsKnowledgeDiscovery(Base):
    """
    知识关系发现
    """
    __tablename__ = "ops_konwledge_discovery"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    sentence    = Column(String(512), nullable=False, comment="原始语句")
    sentity     = Column(String(128), nullable=False, comment="起始实体")
    eentity     = Column(String(128), nullable=False, comment="结束实体")
    rel         = Column(String(128), nullable=False, comment="关系")
    create_tm   = Column(DateTime, default=datetime.now, comment="标记时间")
    flag        = Column(Enum('0', '1', name="e_kn_flag"), default='0', comment='是否提交进入图谱数据库')



    @staticmethod
    def addItem(db, sentence, s, r, e, unique=True):
        ret_oper = False
        if unique and db.query(db.query(OpsKnowledgeDiscovery).filter(OpsKnowledgeDiscovery.sentity==s).filter(OpsKnowledgeDiscovery.rel==r)
            .filter(OpsKnowledgeDiscovery.eentity==e).exists()).scalar():
            ret_oper = True
        else:
            try:
                item = OpsKnowledgeDiscovery()
                item.sentence = sentence
                item.sentity = s
                item.rel = r
                item.eentity = e
                db.add(item)
                db.commit()
                ret_oper = True
            except Exception as e:
                print(e)
                ret_oper = False
        return ret_oper

