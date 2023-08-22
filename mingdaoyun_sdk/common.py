# -*- coding: utf-8 -*-

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

retry_strategy = Retry(
    total=20,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=['HEAD', 'TRACE', 'GET', 'PUT', 'OPTIONS', 'DELETE'],
    backoff_factor=1
)

# 处理个别情况接口重试

adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
# http.verify = f'{base_dir}/cert/cacert.pem'
http.mount("https://", adapter)
http.mount("http://", adapter)
