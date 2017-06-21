# _*_ coding:utf-8 _*_
__author__ = 'caimiao'
__date__ = '15-5-5'

import json
from io import StringIO

from flask import Blueprint, render_template, redirect, url_for, make_response

from archaeology.arghlaborary_operation import ArchlaboraryOperation
from utils.security_helper import UserIdentify
from utils.decorates import login_required
from models.trunck import ProjectProperty

archaeology_app = Blueprint("archaeology", __name__, template_folder="templates")


@archaeology_app.route('/')
@login_required
def Index():
    laborary_operation = ArchlaboraryOperation()
    return render_template("archaeology/_index.html",
                           current_user=UserIdentify.getCurrentUser(),
                           laborary_list=laborary_operation.queryLaborary(),
                           url_create_laborary=url_for(".CreateLaborary"),
                           url_view_laborary=url_for(".ViewLaborary"))

@archaeology_app.route("/create_lab", methods=["POST"])
@login_required
def CreateLaborary():
    """
    创建定量实验室
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.handleCreateLaborary()
    res, _ = laborary_operation.getResponse()
    if res:
        return redirect(url_for(".Index"))
    else:
        return laborary_operation.jumpErrorRedirect("错误", url_for(".Index"))

@archaeology_app.route("/view_lab", methods=["GET"])
@login_required
def ViewLaborary():
    """
    查看定量实验室信息
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.handleViewLaborary()
    res, _ = laborary_operation.getResponse()
    current_user = UserIdentify()
    if res:
        view_data = laborary_operation.getData()
        return render_template("archaeology/_laborary.html",
                               current_user=current_user.getCurrentUser(),
                               laborary=view_data['laborary'],
                               projects=view_data['projects'],
                               url_create_project=url_for(".CreateProject"),
                               url_view_project=url_for(".ViewProject"),
                               url_add_data=url_for(".AjaxFrmAddProjectData"))
    else:
        return laborary_operation.jumpErrorRedirect("错误", url_for(".Index"))


@archaeology_app.route("/create_project", methods=["POST"])
@login_required
def CreateProject():
    """
    创建定量实验项目
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.handleCreateProject()
    res, response = laborary_operation.getResponse()
    if res:
        return redirect(url_for(".ViewLaborary", lid=response['data']['lid']))
    else:
        return laborary_operation.jumpErrorRedirect(jumpurl=url_for(".ViewLaborary", lid=response['data']['lid']))


@archaeology_app.route("/view_project", methods=["GET"])
@login_required
def ViewProject():
    """
    显示定量实验项目
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.viewProject()
    res, _ = laborary_operation.getResponse()
    if res:
        res_data = laborary_operation.getData()
        current_user = UserIdentify()
        return render_template("archaeology/_project.html",
                               current_user=current_user.getCurrentUser(),
                               cls_property=ProjectProperty,
                               view_data_tab=res_data['view_data_tab'],
                               project=res_data['project'],
                               properties=res_data['properties'],
                               url_add_property=url_for(".AddPropertyForProject"),
                               url_load_property_tbl=url_for(".AjaxLoadPropertyTableForProject"),
                               url_del_property=url_for(".AjaxDeletePropertyForProject"),
                               url_load_data_tbl=url_for(".AjaxLoadProjectDataTable"),
                               url_add_data_frm=url_for(".AjaxFrmAddProjectData"),
                               url_describe_data=url_for(".StatisticDescribeDatas", pid=res_data['project']['id']),
                               url_add_data_record=url_for(".AjaxAddProjectDataRecord"),
                               url_print_raw_data=url_for(".GetProjectDataJSON"))
    else:
        return laborary_operation.jumpErrorRedirect(jumpurl=url_for(".Index"))


@archaeology_app.route("/add_property", methods=["POST"])
@login_required
def AddPropertyForProject():
    """
    新增研究项目的数据类型
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.addPorpertyForProject()
    _, response = laborary_operation.getResponse()
    return laborary_operation.jsonEncode(response)

@archaeology_app.route("/ajax_load_property_item", methods=["POST"])
@login_required
def AjaxLoadPropertyItem():
    """
    读取项目属性条目信息
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    property_item = laborary_operation.loadPropertyItem()
    if property_item is not None:
        return render_template("archaeology/_ajax_load/_frm_edit_property.html",
                               cls_property=ProjectProperty,
                               item=property_item)
    else:
        return laborary_operation.jumpErrorRedirect()


@archaeology_app.route("/ajax_loadpropertytbl", methods=["POST"])
@login_required
def AjaxLoadPropertyTableForProject():
    """
    加载研究项目属性表格
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    pid, = laborary_operation.requestParams("pid")
    if laborary_operation.checkParamsAvailable(pid):
        properties = laborary_operation.loadPropertiesOfProject(pid)
        return render_template("archaeology/_ajax_load/_project_property.html",
                               properties=properties,
                               url_load_property_tbl=url_for(".AjaxLoadPropertyTableForProject"),
                               url_del_property=url_for(".AjaxDeletePropertyForProject"),
                               url_set_property_options=url_for(".AjaxFrmAddPropertyOption"),
                               url_modify_property=url_for(".AjaxLoadPropertyItem"))
    else:
        return '<div class="alert alert-danger">实验项目不存在！</div>'

@archaeology_app.route("/ajax_del_property", methods=["POST"])
@login_required
def AjaxDeletePropertyForProject():
    """
    删除研究项目的属性
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.handleDeletePropertyForProject()
    _, response = laborary_operation.getResponse()
    return laborary_operation.jsonEncode(response)


@archaeology_app.route("/ajax_loaddatatbl", methods=["POST"])
@login_required
def AjaxLoadProjectDataTable():
    """
    获取研究项目数据表格
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.prepareForProjectDataTable()
    res, _ = laborary_operation.getResponse()
    if res:
        _res_data = laborary_operation.getData()
        return render_template("archaeology/_ajax_load/_project_data.html",
                               url_update_data_frm=url_for(".AjaxFrmUpdateProjectData"),
                               project=_res_data['project'],
                               properties=_res_data['properties'],
                               url_del_row=url_for(".AjaxDeleteProjectDataRecord"),
                               url_update_row=url_for(".AjaxUpdateProjectDataRecord"),
                               records=_res_data['records'])


@archaeology_app.route("/raw_loaddata", methods=["GET"])
def GetProjectDataJSON():
    """
    获取CSV格式的数据
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.prepareForProjectDataTable()
    res, _ = laborary_operation.getResponse()
    fmt, = laborary_operation.getParams("fmt")

    def _wrap_output_format(result, _fmt):
        '''
        格式化输出数据
        :param _fmt string : json|txt
        '''
        if 'json' == _fmt:
            return json.dumps(result), 200, {'Content-Type': 'text/json; charset=utf-8'}
        elif 'txt' == _fmt:
            stream_io = StringIO()
            _data_lines = []
            _data_lines.append(",".join(result.get("title")))
            for _d in result.get("data", []):
                _data_lines.append(",".join([str(_s_item) for _s_item in _d]))
            stream_io.write("\n".join(_data_lines))
            return stream_io.getvalue(), 200, {'Content-Type': 'text/txt; charset=utf-8'}


    if fmt is None: fmt = 'json'
    if res:
        _res_data = laborary_operation.getData()
        result = {"title": [], "data": []}
        for _h in _res_data['properties']:
            result["title"].append(_h.label)
        for _data_item in _res_data['records']:
            _tmp_array = []
            for _pi in _res_data['properties']:
                if _res_data['records'][_data_item][_pi.label]:
                    _val = _res_data['records'][_data_item][_pi.label].loadValueLabel()
                    _tmp_array.append(float(_val) if _val.isdigit() else _val)
                else:
                    _tmp_array.append("")
            result["data"].append(_tmp_array)
        return _wrap_output_format(result, fmt)



@archaeology_app.route("/project_describe", methods=["GET"])
@login_required
def StatisticDescribeDatas():
    """
    对数据做描述性统计分析
    :return:
    """
    from matplotlib import pyplot as plt
    from pandas import DataFrame

    laborary_operation = ArchlaboraryOperation()
    laborary_operation.prepareForProjectDataTable()
    res, _ = laborary_operation.getResponse()
    if res:
        _res_data = laborary_operation.getData()
        columns = []
        datas = []
        for _h in _res_data['properties']:
            columns.append(_h.label)
        for _data_item in _res_data['records']:
            _tmp_array = []
            for _pi in _res_data['properties']:
                if _res_data['records'][_data_item][_pi.label]:
                    _val = _res_data['records'][_data_item][_pi.label].loadValueLabel()
                    _tmp_array.append(float(_val) if _val.isdigit() else _val)
            datas.append(_tmp_array)
        df = DataFrame(datas, columns=columns)
        fig = plt.figure()
        #ax = fig.add_subplot(1, 1, 1)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        _d = df.describe()
        print("echo describe ......")
        print(_d)
        ax.plot(_d, 'r--')
        for seq in range(0, len(_d)):
            ax.text(seq, _d.values[seq][0], "%s(%s)" % (str(_d.index[seq]), str(_d.values[seq][0])))
        buf = StringIO()
        plt.savefig(buf, dpi=50, fmt="png")
        response = make_response(buf.getvalue())
        response.headers['Content-Type'] = 'Image/png'
        return response


@archaeology_app.route("/ajax_add_data", methods=["GET", "POST"])
@login_required
def AjaxFrmAddProjectData():
    """
    为研究项目添加数据
    :return:
    """
    laboratory_operation = ArchlaboraryOperation()
    pid, = laboratory_operation.postParams("pid")
    properties = laboratory_operation.loadPropertiesOfProject(pid) if laboratory_operation.checkParamsAvailable(pid) else []
    return render_template("archaeology/_ajax_load/_frm_edit_data.html",
                           frm_id='frm_add_project_data',
                           modify='0',
                           properties=properties)

@archaeology_app.route("/ajax_update_data", methods=["GET", "POST"])
@login_required
def AjaxFrmUpdateProjectData():
    '''
    修改研究项目行数据
    :return:
    '''
    laborary_operation = ArchlaboraryOperation()
    pid, rowid = laborary_operation.postParams("pid", "rowid")
    if laborary_operation.checkParamsAvailable(pid, rowid):
        properties = laborary_operation.loadPropertiesOfProject(pid)
        row_items = laborary_operation.loadDataOfProject(pid, rowid)
        return render_template("archaeology/_ajax_load/_frm_edit_data.html",
                               frm_id="frm_update_project_data",
                               row_id=rowid,                # 行编号
                               modify='1',
                               datas=row_items,
                               properties=properties)
    else:
        return laborary_operation.jumpErrorRedirect()

@archaeology_app.route("/add_property_options", methods=["POST"])
@login_required
def AjaxFrmAddPropertyOption():
    """
    为研究项目的属性设置选项
    :return:
    """
    laboraray_operation = ArchlaboraryOperation()
    laboraray_operation.handleSetPropertyOption()
    res, _ = laboraray_operation.getResponse()
    if res:
        return render_template("archaeology/_ajax_load/_frm_edit_property_options.html",
                               property=laboraray_operation.getData(),
                               url_refresh_property_options_tbl=url_for(".AjaxLoadPropertyOptionsList"),
                               url_add_property_options=url_for(".AjaxAddPropertyOptionItem"))
    else:
        return laboraray_operation.ajaxErrorInfoTips()


@archaeology_app.route("/ajax_add_property_option_item", methods=["POST"])
@login_required
def AjaxAddPropertyOptionItem():
    # 添加属性
    laboraray_operation = ArchlaboraryOperation()
    laboraray_operation.handleAddPropertyOption()
    _, response = laboraray_operation.getResponse()
    return laboraray_operation.jsonEncode(response)

@archaeology_app.route("/ajax_add_project_data_record", methods=["POST"])
@login_required
def AjaxAddProjectDataRecord():
    """
    为研究项目添加实验数据
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.handleAddProjectDataRecord()
    _, response = laborary_operation.getResponse()
    return laborary_operation.jsonEncode(response)

@archaeology_app.route("/ajax_update_project_data_record", methods=["POST"])
@login_required
def AjaxUpdateProjectDataRecord():
    """
    更新研究项目的实验室数据
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.handleUpdateProjectDataRecord()
    _, response = laborary_operation.getResponse()
    return laborary_operation.jsonEncode(response)

@archaeology_app.route("/ajax_delete_project_data_record", methods=["POST"])
@login_required
def AjaxDeleteProjectDataRecord():
    """
    删除研究项目的实验室数据
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.handleDeleteProjectDataRecord()
    _, response = laborary_operation.getResponse()
    return laborary_operation.jsonEncode(response)

@archaeology_app.route("/ajax_load_property_option_list", methods=["POST"])
@login_required
def AjaxLoadPropertyOptionsList():
    """
    读取属性选项列表表格
    :return:
    """
    laborary_operation = ArchlaboraryOperation()
    laborary_operation.handleLoadPropertyOptionsOfProperty()
    res, _ = laborary_operation.getResponse()
    if res:
        ret_data = laborary_operation.getData()
        return render_template("archaeology/_ajax_load/_ajax_property_options_list_tbl.html",
                           property=ret_data['property'],
                           options=ret_data['options'])
    else:
        return laborary_operation.ajaxErrorInfoTips()

