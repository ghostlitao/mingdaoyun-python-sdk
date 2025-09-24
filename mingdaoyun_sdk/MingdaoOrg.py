#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Author Todd
@Version 1.0
@Description 明道云组织结构帮助类
"""
import hashlib
import base64
import time
import math

from mingdaoyun_sdk.common import http


class MingdaoOrg:
    appKey = ""
    secretKey = ""
    host = ""
    projectId = ""
    method = "GET"

    # 获取下级成员道云账号Id
    getSubordinateURL = '/api/v2/open/structure/GetSubordinateIds'
    # 添加汇报关系
    addStructuresURL = '/api/v2/open/structure/addStructures'
    # 移除汇报关系
    removeStructuresURL = '/api/v2/open/structure/removeStructures'
    # 替换汇报关系成员
    replaceStructureURL = '/api/v2/open/structure/replaceStructure'

    # 获取用户列表
    getUsersURL = '/generalintegrateapi/v2/user/getUsers'

    params = {}

    # 初始化
    def __init__(self, appKey: str, secretKey: str, host: str, projectId: str):
        """
        初始化mingdaoyun方法

        :param appKey: {string} appKey
        :param secretKey:{string} secretKey
        :param host :{string} host
        :param projectId :{string} projectId
        :return:  Mingdaoyun 实体类
        """
        self.appKey = appKey
        self.secretKey = secretKey
        self.host = host
        self.projectId = projectId
        self.params = {}

    def getSignature(self, appkey, appsecret, timestamp):
        """
        获取签名 timestamp UTC时间戳（精度为毫秒）
        :param appkey:
        :param appsecret:
        :param timestamp:
        :return:
        """
        dict = {"AppKey": appkey, "SecretKey": appsecret,
                "Timestamp": str(timestamp)}
        dict_sort = sorted(dict.items(), key=lambda k: k[0], reverse=False)
        signstr = ''
        for key, value in dict_sort:
            signstr = signstr + '&' + key + '=' + value
        signstr = signstr[1:]
        sha = hashlib.sha256()
        sha.update(signstr.encode("utf-8"))
        sign = str(base64.b64encode(sha.hexdigest().encode("utf-8")), "utf-8")
        return sign

    def exec(self, uri: str):
        if not (self.appKey and self.secretKey and self.projectId and self.host):
            raise Exception('appKey,secretKey,projectId,host is required! ')

        timestamp = int(round(time.time() * 1000))
        auth_param = {
            "timestamp": timestamp,
            "projectId": self.projectId,
            "appKey": self.appKey,
            "sign": self.getSignature(self.appKey, self.secretKey, timestamp)
        }
        url = self.host + uri

        if self.method == "GET":
            data = http.get(url, params={**auth_param, **self.params}).json()
        else:
            data = http.post(url, json={**auth_param, **self.params}).json()
        return data

    def getMySubordinate(self, superiorId: str):
        """
        获取下级成员道云账号Id
        https://www.showdoc.com.cn/mingdao/7372249331332438
        :param superiorId:上级明道云账号Id，不传则代表只取顶级明道云账号Id
        :return:
        """
        self.params["superiorId"] = superiorId
        return self.exec(self.getSubordinateURL)

    def addStructures(self, superior: str, subordinates: list):
        """
        添加汇报关系
        :param superior: 上级的邮箱或手机号，不传则代表添加到顶级
        :param subordinates: 下级成员的邮箱或手机号集合
        :return:
        """
        self.params['superior'] = superior
        self.params['subordinates'] = subordinates
        self.method = "POST"
        return self.exec(self.addStructuresURL)

    def removeStructures(self, subordinates: list):
        """
        移除汇报关系
        :param subordinates: 需要移除的成员邮箱或手机号集合
        :return:
        """
        self.params['subordinates'] = subordinates
        self.method = "POST"
        return self.exec(self.removeStructuresURL)

    def replaceStructure(self, preSubordinate: str, newSubordinate: str):
        """
        替换汇报关系成员
        :param preSubordinate:原成员的邮箱或手机号
        :param newSubordinate:新成员的邮箱或手机号
        :return:
        """
        self.params['preSubordinate'] = preSubordinate
        self.params['subordinates'] = newSubordinate
        self.method = "POST"
        return self.exec(self.replaceStructureURL)

    def getUser(self, userStatus: list = None):
        """
        获取用户列表
        :param userStatus:  用户状态，1:正常 2:被拒绝加入 3:待审核 4:离职
        :return: list[dict]
        """
        if userStatus is None or len(userStatus) == 0:
            userStatus = [1, 2, 3, 4]

        users = []
        self.params.update({"pageSize": 1000})
        self.method = "GET"

        def fetch_page(status, pageIndex):
            self.params.update({"userStatus": status, "pageIndex": pageIndex})
            data = self.exec(self.getUsersURL)
            # 给每个用户打标签
            return [{**u, "userStatus": status} for u in data['data']['users']], data['data']['count']

        for status in userStatus:
            # 第 1 页
            page_users, total = fetch_page(status, 1)
            users.extend(page_users)

            # 后续页
            total_pages = math.ceil(total / self.params['pageSize'])
            for pageIndex in range(2, total_pages + 1):
                page_users, _ = fetch_page(status, pageIndex)
                users.extend(page_users)

        return users