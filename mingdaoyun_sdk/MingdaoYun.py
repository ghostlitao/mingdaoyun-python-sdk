#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Author Todd
@Version 1.0
@Description 明道云API封装类
"""
from mingdaoyun_sdk.common import http


class MingdaoYun:
    appKey = ""
    sign = ""
    host = ""

    worksheetId = ""
    view = ""
    filters = []

    worksheetMap = {}
    params = {}

    # URIs
    APPLICATION_URL = "/api/v1/open/app/get"
    LIST_URL = "/api/v2/open/worksheet/getFilterRows"
    WORKSHEET_MAP_URL = "/api/v2/open/worksheet/getWorksheetInfo"
    GET_BY_ID_URL = "/api/v2/open/worksheet/getRowByIdPost"
    GET_RELATIONS_URL = "/api/v2/open/worksheet/getRowRelations"
    ADD_URL = "/api/v2/open/worksheet/addRow"
    BATCH_ADD_URL = "/api/v2/open/worksheet/addRows"
    DELETE_URL = "/api/v2/open/worksheet/deleteRow"
    EDIT_URL = "/api/v2/open/worksheet/editRow"
    BATCH_EDIT_URL = "/api/v2/open/worksheet/editRows"
    COUNT_URL = "/api/v2/open/worksheet/getFilterRowsTotalNum"

    def __init__(self, appKey: str, sign: str, host: str, cert_path: str = None):
        """
        初始化mingdaoyun方法
        :param appKey: {string} appKey
        :param sign:{string} sign
        :param host :{string} host
        :return:  Mingdaoyun 实体类
        """
        self.appKey = appKey
        self.sign = sign
        self.host = host
        self.params = {}
        self.filters = []
        self.worksheetId = ""
        self.view = ""
        if cert_path is not None:
            http.verify = cert_path
        return

    def reset(self):
        """
        重置class
        :return:
        """
        self.filters = []
        self.params = {}
        self.view = ""

    def table(self, table: str):
        """
        设置当前的worksheet
        :param table: 表名
        :return: 自身
        """
        self.reset()
        self.worksheetId = table
        if not self.worksheetMap.get(self.worksheetId):
            data = self.exec(self.WORKSHEET_MAP_URL)
            map = {}
            for item in data["data"]["controls"]:
                if "alias" in item and item["alias"]:
                    map[item["alias"]] = item
                else:
                    map[item["controlId"]] = item
            self.worksheetMap[self.worksheetId] = map

        return self

    def set_view(self, view: str):
        """
        设置当前的view
        :param view: 表名
        :return: 自身
        """
        self.view = view
        return self

    def applicationInfo(self):
        """
        获取应用信息
        :return:
        """
        data = http.get(self.host + self.APPLICATION_URL, params={'appKey': self.appKey, 'sign': self.sign}).json()
        return data

    def exec(self, uri: str):
        #  如果 api 是官方的，需要改下地址  https://api.mingdao.com/v2/open/worksheet/getFilterRows
        if 'api.mingdao.com' in self.host:
            uri = uri.replace('/api/v2/open/', '/v2/open/')

        if not (self.appKey and self.sign and self.worksheetId):
            raise Exception('appKey,sign,table is required! ')
        auth_prams = {"appKey": self.appKey, "sign": self.sign, "worksheetId": self.worksheetId}
        if len(self.view) > 0:
            self.params["viewId"] = self.view
        self.params["filters"] = self.filters
        data = http.post(self.host + uri, json={**self.params, **auth_prams}).json()
        return data

    def get_field_data_type(self, field: str) -> str:
        """
        或者字段类型
        :param field:
        :return:
        """
        map = self.worksheetMap[self.worksheetId]
        if field in map and map[field]:
            return map[field]["type"]

    def where(self, field: str, symbol: str, value='', values=[], minValue="", maxValue=""):
        """
        设置查询条件
        :param field: 字段
        :param symbol: 操作符，支持 contains , = , startWith, endWith , notContain , != ,is null(None), not null , > ,>=,  <, <=, RCEq , RCNe ,between , nBetween,DateEnum,NDateEnum,DateBetween,DateNBetween
        :param value: 值
        :param values: 数组类型的值
        :param maxValue: 最大值
        :param minValue: 最小值
        :return: 自身
        """

        if symbol is None or symbol == "is null":
            filter_type = 7
        elif symbol == "not null":
            filter_type = 8
        elif symbol == "contains":
            filter_type = 1
        elif symbol == "=":
            filter_type = 2
        elif symbol == "startWith":
            filter_type = 3
        elif symbol == "endWith":
            filter_type = 4
        elif symbol == "notContain":
            filter_type = 5
        elif symbol == "!=":
            filter_type = 6
        elif symbol == "between":
            filter_type = 11
        elif symbol == "nBetween":
            filter_type = 12
        elif symbol == ">":
            filter_type = 13
        elif symbol == ">=":
            filter_type = 14
        elif symbol == "<":
            filter_type = 15
        elif symbol == "<=":
            filter_type = 16
        elif symbol == "DateEnum":
            # 日期是
            filter_type = 17
        elif symbol == "NDateEnum":
            # 日期不是
            filter_type = 18
        elif symbol == "DateBetween":
            # 在范围内
            filter_type = 31
        elif symbol == "DateNBetween":
            # 不在范围内
            filter_type = 32
        elif symbol == "DateGt":
            filter_type = 33
        elif symbol == "DateGte":
            filter_type = 34
        elif symbol == "DateLt":
            filter_type = 35
        elif symbol == "DateLte":
            filter_type = 36
        elif symbol == "RCEq":
            # 关系相等
            filter_type = 24
        elif symbol == "RCNe":
            # 关系不相等
            filter_type = 25
        else:
            filter_type = symbol

        _filter = {
            'controlId': field,
            'dataType': self.get_field_data_type(field),
            'spliceType': 1,
            'filterType': filter_type,
        }
        if symbol in ["DateBetween", "DateNBetween"]:
            _filter["maxValue"] = maxValue
            _filter["minValue"] = minValue
        if len(values) > 0:
            _filter["values"] = values
        else:
            _filter["value"] = value
        self.filters.append(_filter)
        return self

    def find(self, rowid=None, pageSize=1000, pageIndex=1, all=False):
        """
        查询数据
        :param rowid:
        :param pageSize:
        :param pageIndex:
        :param all:
        :return:
        """
        if rowid:
            # 找单个
            self.params["rowId"] = rowid
            return self.exec(self.GET_BY_ID_URL)
        else:
            self.params["pageSize"] = pageSize
            self.params["pageIndex"] = pageIndex
            self.params["notGetTotal"] = 1  # 不要Total 提高性能
            # 根据条件进行搜索
            result = self.exec(self.LIST_URL)
            if all:
                # 获取全部
                while True:
                    self.params["pageIndex"] = self.params["pageIndex"] + 1
                    current_result = self.exec(self.LIST_URL)
                    if len(current_result["data"]["rows"]) > 0:
                        result["data"]["rows"] = result["data"]["rows"] + current_result["data"]["rows"]
                    else:
                        break
                result["data"]["total"] = len(result["data"]["rows"])
                return result
            else:
                result["data"]["total"] = len(result["data"]["rows"])
                return result

    def add(self, data: list):
        """
        新增一条数据,data 格式为：
        data = [{'controlId': $controlId,'value':$value},{'controlId': $controlId,'value':$value}]
        :param data:
        :return:
        """
        self.params["controls"] = data
        return self.exec(self.ADD_URL)

    def batch_add(self, data: list):
        """
        新增多条数据,data 格式为：
        data = [[{'controlId': $controlId,'value':$value},{'controlId': $controlId,'value':$value}],
                [{'controlId': $controlId,'value':$value},{'controlId': $controlId,'value':$value}]]
        :param data:
        :return:
        """
        self.params["rows"] = data
        return self.exec(self.BATCH_ADD_URL)

    def delete(self, rowid: str):
        """
        删除记录，rowid 为逗号拼接的字符串
        :param rowid:
        :return:
        """
        self.params["rowId"] = rowid
        return self.exec(self.DELETE_URL)

    def find_relations(self, rowid, controlId, pageSize=1000, pageIndex=1, all=False):
        """
        查询数据
        :param rowid: 本表rowid
        :param controlId: 关联字段
        :param pageSize: 页码
        :param pageIndex:
        :param all:
        :return:
        """
        self.params["pageSize"] = pageSize
        self.params["pageIndex"] = pageIndex
        self.params["rowId"] = rowid
        self.params["controlId"] = controlId
        # 根据条件进行搜索
        result = self.exec(self.GET_RELATIONS_URL)
        if all:
            # 获取全部
            while len(result["data"]["rows"]) < result["data"]["total"]:
                print(f'turn page {len(result["data"]["rows"])}/{result["data"]["total"]}')
                self.params["pageIndex"] = self.params["pageIndex"] + 1
                current_result = self.exec(self.GET_RELATIONS_URL)
                result["data"]["rows"] = result["data"]["rows"] + current_result["data"]["rows"]
            return result
        else:
            return result

    def sort(self, sortId: str, isAsc: bool):
        """
        设置排序
        :param sortId:
        :param isAsc:
        :return:
        """
        self.params["sortId"] = sortId
        self.params["isAsc"] = isAsc
        return self

    def edit(self, rowid: str, controls: list):
        """
        编辑一条数据
        :param rowid:
        :param controls:
        :return:
        """
        self.params["rowId"] = rowid
        self.params["controls"] = controls
        return self.exec(self.EDIT_URL)

    def batch_edit(self, rowids: list, control: dict):
        """
        编辑多条数据
        :param rowids:
        :param control:
        :return:
        """
        self.params["rowIds"] = rowids
        self.params["control"] = control
        return self.exec(self.BATCH_EDIT_URL)

    def count(self):
        """
        获取数量
        :return:
        """
        return self.exec(self.COUNT_URL)

    def triggerWorkflow(self, value=True):
        """
        设置是否触发工作流 , 默认触发
        :param value:
        :return:
        """
        self.params["triggerWorkflow"] = value
        return self

    def notGetTotal(self, value=False):
        """
        是否不统计总行数以提高性能
        :param value:
        :return:
        """
        self.params["notGetTotal"] = value
        return self

    def useControlId(self, value=False):
        """
        是否只返回controlId，默认false
        :param value:
        :return:
        """
        self.params["useControlId"] = value
        return self

    def getSystemControl(self, value=False):
        """
        是否获取系统字段，默认false
        :param value:
        :return:
        """
        self.params["getSystemControl"] = value
        return self
