from mingdaoyun_sdk.common import http


class MingdaoYunV3:
    appKey = ""
    sign = ""
    host = ""
    applicationInfo = {}

    worksheetId = ""
    view = ""
    filters = []

    worksheetMap = {}
    workflowMap = {}
    params = {}

    # URIs
    APPLICATION_URL = "/api/v3/app"
    WORKSHEET_MAP_URL = "/api/v3/app/worksheets/{worksheet_id}"
    WORKFLOW_LIST_URL = "/api/v3/app/workflow/processes"
    WORKFLOW_DETAIL_URL = "/api/v3/app/workflow/processes/{process_id}"

    def __init__(self, appKey: str, sign: str, host: str, cert_path: str = None, proxy:dict=None):
        """
        初始化mingdaoyun方法
        :param appKey: {string} appKey
        :param sign:{string} sign
        :param host :{string} host
        :return:  Mingdaoyun 实体类
        """

        self.headerParameters = {
            'HAP-Appkey': appKey,
            'HAP-Sign': sign,
            'user-agent': 'mingdaoyun-python-sdk/0.0.16'
        }

        self.host = host
        self.get_application_info()
        self.workflow()
        self.params = {}
        self.filters = []
        self.worksheetId = ""
        self.view = ""
        if proxy is not None:
            http.proxies = proxy
        if cert_path is not None:
            http.verify = cert_path
        return


    def get_application_info(self):
        """
        获取应用信息
        :return: 应用信息
        """
        url = self.host + self.APPLICATION_URL
        try:
            data = http.get(url, headers=self.headerParameters)
            if data.status_code == 200:
                self.applicationInfo = data.json()
            else:
                raise Exception("请求失败")
        except Exception as e:
            raise Exception('获取应用信息失败, 错误信息:{}'.format(e))
        return self

    def table(self, table: str):
        """
        设置当前的worksheet
        :param table: 表名
        :return: 自身
        """
        self.worksheetId = table
        if not self.worksheetMap.get(self.worksheetId):
            data = self.exec("GET",self.host+self.WORKSHEET_MAP_URL.replace("{worksheet_id}", self.worksheetId))
            map = {}
            for item in data["data"]["fields"]:
                if "alias" in item and item["alias"]:
                    map[item["alias"]] = item
                else:
                    map[item["id"]] = item
            self.worksheetMap[self.worksheetId] = map

        return self

    def exec(self,method,url,params: dict=None):
        """
        执行请求
        :param method: 请求方法
        :param url: 请求url
        :param params: 请求参数
        :return: 请求结果
        """
        if self.proxies is not None:
            http.proxies = self.proxies
        if method == 'GET':
            data = http.get(url, headers=self.headerParameters, params=params).json()
        elif method=='POST':
            if params is None or params=={}:
                raise Exception("请传入参数")
            data = http.post(url, headers=self.headerParameters, json=params).json()
        else:
            raise Exception("不支持的请求方法")
        return data

    def workflow(self):
        """
        设置当前的workflow
        :return: 自身
        """

        data = self.exec("GET",self.host+self.WORKFLOW_LIST_URL)
        map = {}
        for item in data["data"]["controls"]:
            if "alias" in item and item["alias"]:
                map[item["alias"]] = item
            else:
                map[item["controlId"]] = item
        self.workflowMap[self.workflowId] = map
        return self

    def get_workflow_detail(self, workflowId: str):
        """
        获取workflow详情
        :param workflowId: workflowId
        :return: workflow详情
        """
        if not self.workflowMap.get(workflowId):
            self.workflow()

if __name__ == '__main__':
    mdy = MingdaoYunV3("490908b1abd517ed", "NDhjZDQyYzAxNzA5NjZkMzhiZjY0Nzc4ZGNhMDhhNTcxMTI3ZjQ5ZWMwYjk0MGQ5MDZmNDBkMGZkY2RiM2Q3OQ==", "http://ddns.rinsys.com:8880/")

    print(mdy.workflowMap)
