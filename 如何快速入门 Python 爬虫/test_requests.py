# -*- coding: utf-8 -*-
# @File  : test_requests.py
# @Author: AaronJny
# @Date  : 2019/11/13
# @Desc  :
from bs4 import BeautifulSoup
import requests

# 使用requests类库发起一次http GET请求
resp = requests.get('https://www.baidu.com')
# resp是请求的响应对象，查看响应状态码
print(resp.status_code)
# 查看返回的网页源码
print(resp.content.decode('utf-8'))

# 将网页源码构造成BeautifulSoup对象，方便操作
bsobj = BeautifulSoup(resp.content, 'lxml')
# 获取网页中的所有a标签对象
a_list = bsobj.find_all('a')
# 创建一个空列表，用来存储所有的超链接
urls = []
# 对于每一个a标签
for a in a_list:
    # 提取a标签对象的href属性，即这个对象指向的链接地址
    href = a.get('href')
    # 将它加入到列表中
    urls.append(href)
# 将所有链接使用'\n'拼接成一个字符串
text = '\n'.join(urls)
# 写入到文件中去
with open('urls.txt', 'w', encoding='utf-8') as f:
    f.write(text)