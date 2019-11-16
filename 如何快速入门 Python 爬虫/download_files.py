# -*- coding: utf-8 -*-
# @File    : download_files.py
# @Author  : AaronJny
# @Date    : 2019/11/13
# @Desc    :
import requests

# 文件地址
url = 'https://www.js-lottery.com/PlayZone/downLottoData.html'
# 使用requests请求文件数据
resp = requests.get(url)
# 以二进制的方式创建一个csv文件
with open('lotto.csv', 'wb') as f:
    # 并将获取到的二进制数据写入到文件中
    f.write(resp.content)
