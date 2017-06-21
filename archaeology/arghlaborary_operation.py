# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-6-24'

from uuid import uuid1

from sqlalchemy import or_

from utils.http_helper import BaseOperations
from utils.security_helper import UserIdentify
from models import db_session
from models.trunck import Laborary, Project, ProjectProperty, PropertyOptions, ProjectItem


class ArchlaboraryOperation(BaseOperations):
    """
    定量实验室相关逻辑操作
    """
    def handleCreateLaborary(self):
        """
        处理创建实验室功能
        :return:
        """
        name, unit, desc = self.postParams("name", "unit", "desc")
        if self.checkParamsAvailable(name):
            current_user = UserIdentify()
            same_name_item = db_session.query(Laborary).filter(Laborary.name==name).exists()
            if not db_session.query(same_name_item).scalar():
                try:
                    new_laborary = Laborary()
                    new_laborary.name = name
                    new_laborary.desc = desc
                    new_laborary.unit = unit
                    new_laborary.u_id = current_user.uid
                    db_session.add(new_laborary)
                    db_session.commit()
                    self.changeResponse2Success()
                except Exception as e:
                    db_session.rollback()
                    self.setFailureReason(str(e))
            else:
                self.setFailureReason("已经存在同名的定量实验室！")

    def queryLaborary(self):
        """
        查询所属的定量实验室列表
        :return: List
        """
        current_user = UserIdentify()
        laborary_records = db_session.query(Laborary).filter(Laborary.u_id==current_user.uid).all()
        laborary_list = []
        for _rcd in laborary_records:
            laborary_list.append(_rcd.toDict())
        return laborary_list

    def handleViewLaborary(self):
        """
        提取展示定量实验室需要的数据
        :return:
        """
        lid, = self.getParams("lid")
        if self.checkParamsAvailable(lid):
            view_datas = {}
            laborary_item = db_session.query(Laborary).filter(Laborary.id==lid).first()
            if laborary_item is not None:
                projects_list = db_session.query(Project).filter(Project.l_id==lid).all()

                view_datas['projects'] = projects_list
                view_datas['laborary'] = laborary_item.toDict()
                self.setData(view_datas)
                self.changeResponse2Success()

    def handleCreateProject(self):
        """
        创建指定实验室下的定量实验项目
        :return:
        """
        lid, pname, pdesc = self.postParams("lid", "pname", "pdesc")
        self.setData({'lid': lid})
        if self.checkParamsAvailable(lid, pname):
            project_exists_query = db_session.query(Project).filter(Project.name==pname).\
                filter(Project.l_id==lid).exists()
            if not db_session.query(project_exists_query).scalar():
                try:
                    new_project = Project()
                    new_project.l_id = lid
                    new_project.name = pname
                    new_project.desc = pdesc
                    db_session.add(new_project)
                    db_session.commit()
                    self.changeResponse2Success()
                except Exception as e:
                    db_session.rollback()
                    self.setFailureReason(str(e))
            else:
                self.setFailureReason("该实验室下存在同名的定量研究项目，请重新命名！")

    def viewProject(self):
        """
        查询所有项目列表
        :return:
        """
        pid, = self.getParams("pid")
        if self.checkParamsAvailable(pid):
            res_info = {}
            project_item = db_session.query(Project).filter(Project.id==pid).first()

            if project_item is not None:
                data_exists = db_session.query(ProjectItem).filter(ProjectItem.proj_id==project_item.id).exists()
                properties = db_session.query(ProjectProperty).filter(ProjectProperty.p_id==project_item.id).all()
                res_info.setdefault('project', project_item.toDict())
                res_info.setdefault('properties', properties)
                res_info.setdefault('view_data_tab', db_session.query(data_exists).scalar())
                self.changeResponse2Success()
                self.setData(res_info)
            else:
                self.setFailureReason("定量实验项目不存在！")

    def addPorpertyForProject(self):
        """
        添加字段属性
        :return:
        """
        pid, name, label, _type, desc = self.postParams("pid", "name", "label", "type", "desc")
        if self.checkParamsAvailable(pid, name, label, _type, desc):
            project_exists = db_session.query(Project).filter(Project.id==pid).exists()
            if db_session.query(project_exists).scalar():
                try:
                    project_property = ProjectProperty()
                    project_property.name = name
                    project_property.label = label
                    project_property.type = _type
                    project_property.desc = desc
                    project_property.p_id = pid
                    db_session.add(project_property)
                    db_session.commit()
                    self.changeResponse2Success()
                except Exception as e:
                    db_session.rollback()
                    self.setFailureReason(str(e))
            else:
                self.setFailureReason("父级实验项目不存在！")

    def loadPropertyItem(self):
        '''
        获取项目字段属性
        :param prop_id:
        :return:
        '''
        prop_id, = self.postParams("prop_id")
        if self.checkParamsAvailable(prop_id):
            return db_session.query(ProjectProperty).filter(ProjectProperty.id==prop_id).first()


    def loadPropertiesOfProject(self, pid):
        """
        读取指定id项目下的字段属性列表
        :param pid:
        :return:
        """
        project_exists = db_session.query(Project).filter(Project.id==pid).exists()
        return db_session.query(ProjectProperty).filter(ProjectProperty.p_id==pid).all() \
                if db_session.query(project_exists).scalar() else []

    def loadDataOfProject(self, pid, rowid):
        '''
        读取指定id和行编号的项目数据
        :param pid:
        :param rowid:
        :return:
        '''
        ret_item_list = {}
        p_item_list = db_session.query(ProjectItem).filter(ProjectItem.proj_id==pid).filter(ProjectItem.row_id==rowid).all()
        for _item in p_item_list:
            ret_item_list.setdefault(_item.label, _item)
        return ret_item_list

    def handleDeletePropertyForProject(self):
        """
        删除指定的研究项目属性
        :return:
        """
        _id, = self.postParams("id")
        if self.checkParamsAvailable(_id):
            try:
                _del_property = db_session.query(ProjectProperty).filter(ProjectProperty.id==_id).first()
                if _del_property is not None:
                    db_session.query(ProjectItem.proj_id==_del_property.p_id).filter(ProjectItem.label==_del_property.label).delete()
                    db_session.delete(_del_property)
                    db_session.commit()
                    self.changeResponse2Success()
            except Exception as e:
                db_session.rollback()
                self.setFailureReason(str(e))

    def prepareForProjectDataTable(self):
        """
        为实验项目数据表格
        :return:
        """
        def _arrangeProjectDatas(_data_collection):
            _middle_arrange = {}
            for _raw_data in _data_collection:
                if not _raw_data.row_id in _middle_arrange:
                    _middle_arrange[_raw_data.row_id] = {}
                _middle_arrange[_raw_data.row_id].setdefault(_raw_data.label, _raw_data)

            for _middle_data in _middle_arrange:
                for _property in properties:
                    if not _property.label in _middle_arrange[_middle_data]:
                        _middle_arrange[_middle_data][_property.label] = None

            return _middle_arrange

        # TODO 组合项目数据表格，使body和head对应
        pid, = self.requestParams("pid")
        if self.checkParamsAvailable(pid):
            project = db_session.query(Project).filter(Project.id==pid).first()
            if project is not None:
                project_data = {}
                properties = db_session.query(ProjectProperty).filter(ProjectProperty.p_id==pid).all()
                data_records = db_session.query(ProjectItem).filter(ProjectItem.proj_id==pid).all()
                project_data.setdefault('project', project)
                project_data.setdefault('properties', properties)
                project_data.setdefault('records', _arrangeProjectDatas(data_records))

                self.setData(project_data)
                self.changeResponse2Success()
            else:
                self.setFailureReason("实验项目不存在！")



    def handleSetPropertyOption(self):
        """
        获取属性字段的内容，处理属性选项字段的设置功能
        :return:
        """
        pid, = self.postParams("pid")
        if self.checkParamsAvailable(pid):
            property = db_session.query(ProjectProperty).filter(ProjectProperty.id==pid).first()
            if property is not None:
                self.setData(property)
                self.changeResponse2Success()

    def handleAddPropertyOption(self):
        """
        添加属性选项字段
        :return:
        """
        name, label, weight, opid = self.postParams("oname", "oid", "oweight", "opid")
        if self.checkParamsAvailable(name, label, opid):
            conflict_exists = db_session.query(PropertyOptions).filter(PropertyOptions.p_id==opid).\
                filter(or_(PropertyOptions.name==name, PropertyOptions.label==label)).exists()
            if not db_session.query(conflict_exists).scalar():
                try:
                    po = PropertyOptions()
                    po.name = name
                    po.label = label
                    po.weight = weight if weight is not None else 0
                    po.p_id = opid
                    db_session.add(po)
                    db_session.commit()
                    self.changeResponse2Success()
                except Exception as e:
                    db_session.rollback()
                    self.setFailureReason(str(e))
            else:
                self.setFailureReason("选项名称或选项编号冲突！")

    def handleLoadPropertyOptionsOfProperty(self):
        """
        获取指定属性下的所有属性选项
        :return:
        """
        pid, = self.postParams("pid")

        if self.checkParamsAvailable(pid):
            property = db_session.query(ProjectProperty).filter(ProjectProperty.id==pid).first()
            if property is not None:
                ret_data = {}
                options_list = db_session.query(PropertyOptions).filter(PropertyOptions.p_id==pid).all()
                ret_data.setdefault('property', property)
                ret_data.setdefault('options', options_list)
                self.setData(ret_data)
                self.changeResponse2Success()
            else:
                self.setFailureReason("字段属性不存在！")


    def handleAddProjectDataRecord(self):
        _data_dict = self.postParams("*")
        if "pid" in _data_dict:
            try:
                project_id = int(_data_dict.get('pid'))
            except Exception as e:
                project_id = 0
            if project_id > 0:
                row_num = str(uuid1())
                try:
                    for _d in _data_dict:
                        if "pid" != _d:
                            pproperty_item = db_session.query(ProjectProperty).\
                                filter(ProjectProperty.label==_d).\
                                filter(ProjectProperty.p_id==project_id).first()
                            if pproperty_item is not None:
                                p_item = ProjectItem()
                                p_item.label = _d
                                p_item.value = _data_dict[_d]
                                p_item.row_id = row_num
                                p_item.proj_id = project_id
                                p_item.p_id = pproperty_item.id
                                db_session.add(p_item)
                    db_session.commit()
                    self.changeResponse2Success()
                except Exception as e:
                    db_session.rollback()
                    self.setFailureReason(str(e))

    def handleDeleteProjectDataRecord(self):
        '''
        删除研究项目中的一行数据
        :return:
        '''
        pid, row_id = self.postParams("pid", "row_id")
        if self.checkParamsAvailable(pid, row_id):
            try:
                db_session.query(ProjectItem).filter(ProjectItem.proj_id==pid).filter(ProjectItem.row_id==row_id).delete()
                db_session.commit()
                self.changeResponse2Success()
            except Exception as e:
                db_session.rollback()


    def handleUpdateProjectDataRecord(self):
        '''
        更新研究项目中的一行数据
        :return:
        '''
        _data_dict = self.postParams("*")
        if "pid" in _data_dict and "row_id" in _data_dict:
            try:
                project_id = int(_data_dict.get("pid", 0))
                row_id = _data_dict.get("row_id", '')
            except Exception:
                project_id = 0
            if project_id > 0 and '' != row_id:
                try:
                    db_session.query(ProjectItem).filter(ProjectItem.proj_id==project_id).filter(ProjectItem.row_id==row_id).delete()
                    for _d in _data_dict:
                        if "pid" != _d and "row_id" != _d:
                            pproperty_item = db_session.query(ProjectProperty).filter(ProjectProperty.label==_d).first()
                            if pproperty_item is not None:
                                p_item = ProjectItem()
                                p_item.label = _d
                                p_item.value = _data_dict[_d]
                                p_item.row_id = row_id
                                p_item.proj_id = project_id
                                p_item.p_id = pproperty_item.id
                                db_session.add(p_item)
                    db_session.commit()
                    self.changeResponse2Success()
                except Exception as e:
                    db_session.rollback()
                    self.setFailureReason(str(e))
        else:
            self.setFailureReason('缺少关键参数！')
