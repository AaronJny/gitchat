# -*- coding: utf-8 -*-
# @File    : test_headers.py
# @Author  : AaronJny
# @Date    : 2019/11/14
# @Desc    :
import requests
from pprint import pprint

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
}

url = 'http://httpbin.org/headers'
resp = requests.get(url, headers=headers)
pprint(resp.json())
