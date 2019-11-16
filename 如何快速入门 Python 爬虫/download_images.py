# -*- coding: utf-8 -*-
# @File    : download_images.py
# @Author  : AaronJny
# @Date    : 2019/11/13
# @Desc    : 使用Python保存图片的实例
import requests

# 图片地址
url = 'http://www.baidu.com/img/bd_logo1.png?qua=high'
# 使用requests请求图片数据
resp = requests.get(url)
# 以二进制的方式创建一个png图片文件
with open('logo.png', 'wb') as f:
    # 并将获取到的二进制图片数据写入到文件中
    f.write(resp.content)
