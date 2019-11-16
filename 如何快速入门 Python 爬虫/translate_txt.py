# -*- coding: utf-8 -*-
# @File    : translate_txt.py
# @Author  : AaronJny
# @Date    : 2019/11/15
# @Desc    : 将小说从数据库中读出，并转成txt文件
from datetime import datetime
import os
import pymysql


def query(conn, sql):
    """
    使用给定数据库连接conn查询sql,并返回查询结果
    :param conn: 数据库连接
    :param sql: 待查询sql
    :return: list[dict]，查询结果
    """
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    res = cursor.fetchall()
    return res


# 创建数据库连接
conn = pymysql.connect(host="localhost", port=3306, user='root', password='123456', db='spider')
# 读取全部小说信息
sql = """
select * from spider.novels
"""
novels = query(conn, sql)
# 小说描述模板
description_format = '书名：{novel_name}\n作者：{author}\n字数：{novel_characters}K\n' \
                     '最后更新时间：{update_time_str}\n小说状态：{novel_status}\n原始链接：{url}\n\n'
# 创建保存小说的文件夹
if not os.path.exists('novels'):
    os.mkdir('novels')
# 对于每一本小说
for novel in novels:
    # 小说文本列表
    novel_contents = []
    # 生成小说描述
    description = description_format.format(
        update_time_str=datetime.fromtimestamp(novel['update_time']).strftime('%Y-%m-%d'), **novel)
    # 将描述加入文本列表
    novel_contents.append(description)
    # 加入分割线
    novel_contents.append('\n{}\n'.format('-' * 40))
    # 读取全部小数章节
    sql = """
    select * from spider.chapters where novel_id={}
    """.format(novel['novel_id'])
    chapters = query(conn, sql)
    # 先对小说章节进行排序
    chapters = sorted(chapters, key=lambda x: x['chapter_order'])
    # 逐个对小说章节进行处理
    for chapter in chapters:
        # 将章节名称加入文本列表
        novel_contents.append('{}\n\n'.format(chapter['chapter_name']))
        # 将小说内容加入文本列表
        novel_contents.append('{}\n\n'.format(chapter['chapter_content']))
        # 加入分割线
        novel_contents.append('\n{}\n'.format('-' * 40))
    # OK，保存小说
    with open('novels/{}.txt'.format(novel['novel_name']), 'w', encoding='utf-8') as f:
        f.write(''.join(novel_contents))
# 关闭数据库
conn.close()
