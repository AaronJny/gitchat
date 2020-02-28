# -*- coding: utf-8 -*-
# @File    : x23us_spider.py
# @Author  : AaronJny
# @Date    : 2019/11/13
# @Desc    : 顶点小说网爬虫
from datetime import datetime
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pymysql
import requests


class MySQLOperator:
    """
    MySQL操作器，用来完成数据的写入
    """

    def __init__(self):
        # 保存不同种类数据的字典
        self.item_dict = {}
        # 批量写入数据库的批大小
        self.batch_size = 100

    @classmethod
    def create_conn(cls, db='spider'):
        """
        创建并返回一个数据库连接
        :return:
        """
        conn = pymysql.connect(host="localhost", port=3306, user='root', password='123456', db=db)
        return conn

    def insert_many(self, table_name, items):
        """
        将给定的数据列表items，批量写入到table_name表中
        :param table_name:数据表名
        :param items: 待写入的数据列表
        :return:
        """
        item = items[0]
        # 提取数据表的全部字段名称
        keys = sorted(item.keys())
        # 构建写入用的sql
        sql_format = """
                insert into {table_name}({keys_str}) values({placeholder}) on duplicate key update {update_str}
                """
        keys_str = ','.join(keys)
        placeholder = ','.join('%s' for _ in keys)
        update_str = ','.join(['{key}=values({key})'.format(key=key) for key in keys])
        sql = sql_format.format(table_name=table_name, keys_str=keys_str, placeholder=placeholder,
                                update_str=update_str)
        # 构建插入数据库用的数据格式,保重sql中键的顺序和值的顺序一致
        records = [[item[key] for key in keys] for item in items]
        # 创建连接，执行写入
        conn = self.create_conn()
        cursor = conn.cursor()
        cursor.executemany(sql, records)
        cursor.close()
        conn.commit()
        conn.close()

    def flush_to_db(self):
        """
        将数据刷写到数据库中。
        为了保证数据库写入性能，我们只当缓存到一定数量的数据时，才批量写入数据库
        :return:
        """
        # 对于每一个数据表缓存数据
        for table_name, items in self.item_dict.items():
            # 如果已经缓存了足够数量
            if len(items) >= self.batch_size:
                # 就批量写入数据库
                self.insert_many(table_name, items)
                # 并清空此数据表的缓存
                self.item_dict[table_name].clear()

    def add(self, table_name, item):
        """
        将一个采集数据保存到数据库的指定数据表中
        :param table_name: 表名
        :param item:
        :return:
        """
        # 在item_dict中查找是否有table_name这个键，如果没有，就创建，指向的value为一个空list
        # 将采集到的一条数据加入到item_dict[table_name]指向的list中
        self.item_dict.setdefault(table_name, []).append(item)
        # 所有的数据在上一步被缓存到内存里面，接着调用刷写到数据库的方法
        self.flush_to_db()

    def close(self):
        """
        关闭操作器时的收尾操作
        :return:
        """
        # 检查是否还有没写入数据库的缓存数据
        self.batch_size = 1
        # 有就写入
        self.flush_to_db()


class X23usSpider:

    def __init__(self):
        # 列表页url模板
        self.list_page_url_format = 'https://www.ydshu.com/quanben/{page}'
        # 要采集的总页数
        self.total_page = 1
        # 数据库操作器，用来保存数据到数据库
        self.mysql_operator = MySQLOperator()

    def replace_br(self, content):
        """
        将content中的br标签，替换成\n+br，以保证换行被正确保留
        :param content:
        :return:
        """
        html = content.decode('gbk')
        html = re.sub('<[ ]*br[ ]*/[ ]*>', '\n<br>', html)
        return html

    def download_and_parse_chapter_page(self, chapter_url, novel_url):
        """
        下载并解析小说章节内容
        :param chapter_url: 小说章节地址
        :param novel_url: 小说主页地址
        :return: str,章节内容
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Referer': novel_url,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        # 发起请求
        resp = requests.get(chapter_url, headers=headers)
        # 解析章节内容
        html = self.replace_br(resp.content)
        bsobj = BeautifulSoup(html, 'lxml')
        content = bsobj.find('dd', {'id': 'contents'}).get_text()
        content = content.replace('\xa0', ' ')
        return content

    def download_and_parse_novel_page(self, novel_url, novel_id):
        """
        下载并解析小说主页，提取章节地址，进一步调用方法获取章节内容
        :param novel_url: 小说主页地址
        :param novel_id: 小说在网站上的编号
        :return:
        """
        # 请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Referer': self.list_page_url_format.format(page=1),
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        # 获取页面源码
        resp = requests.get(novel_url, headers=headers)
        # 解析章节列表
        bsobj = BeautifulSoup(resp.content, 'lxml')
        chapter_tags = bsobj.find('table', {'id': 'at'}).find_all('a')
        # 逐个解析章节信息
        for index, chapter_tag in enumerate(chapter_tags):
            # enumerate的作用是在遍历可迭代对象时生成一个递增的计数器，index依次为1,2,3,4...
            # 开始解析章节信息
            # 解析章节地址
            chapter_url_short = chapter_tag.get('href')
            # urljoin('https://www.ydshu.com/html/76/76609/','34183392.html')=='https://www.ydshu.com/html/76/76609/34183392.html'
            chapter_url = urljoin(novel_url, chapter_url_short)
            # 解析章节id
            chapter_id = chapter_url_short.split('.')[0]
            # 解析章节名称
            chapter_name = chapter_tag.get_text()
            # 请求病解析章节内容
            chapter_content = self.download_and_parse_chapter_page(chapter_url, novel_url)
            # 组合数据
            chapter = {
                'chapter_id': chapter_id,
                'novel_id': novel_id,
                'chapter_name': chapter_name,
                'chapter_order': index,
                'chapter_content': chapter_content,
                'url': chapter_url
            }
            print(chapter_name)
            # 将数据写入数据库
            self.mysql_operator.add('chapters', chapter)

    def download_and_parse_list_page(self, page):
        """
        下载并解析小说列表页，保存小说数据，并进一步访问其小说主页
        :param page: 列表页页码
        :return:
        """
        # 生成列表页地址
        list_page_url = self.list_page_url_format.format(page=page)
        # 请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            # Referer表明你是从哪个页面跳转过来的，是用于防盗链的一种手段，有时也会被用于反爬虫
            'Referer': self.list_page_url_format.format(page=''),
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        # 发起请求
        resp = requests.get(list_page_url, headers=headers)
        # 使用网页源码构建BeautifulSoup对象
        bsobj = BeautifulSoup(resp.content, 'lxml')
        # 使用浏览器对元素进行检查，先定位到保存小说信息的表格。
        # 每一行(每一个tr就是一本小说的信息)
        # 注意，如果这一步不是很理解，请浏览一下BeautifulSoup的文档，非常简单
        trs = bsobj.find('dl', {'id': 'content'}).find('table').find_all('tr')
        # 从第二行开始(第一行是表格的标题)
        for tr in trs[1:]:
            # 开始提取这部小说的信息
            tds = tr.find_all('td')
            # 解析小说的名称
            novel_name = tds[0].find_all('a')[1].get_text()
            # 解析小说的url
            novel_url = tds[0].find_all('a')[1].get('href')
            # 解析小说id
            novel_id = novel_url.split('/')[-2]
            # 解析小说作者
            author = tds[2].get_text()
            # 解析小说字数
            novel_characters = tds[3].get_text().replace('K', '')
            # 解析小说最后更新时间
            update_time_str = tds[4].get_text()
            # 转成时间戳
            update_time_int = int(datetime.strptime('20' + update_time_str, '%Y-%m-%d').timestamp())
            # 解析小说状态
            novel_status = tds[5].get_text()
            # 组合数据
            novel = {
                'novel_id': novel_id,
                'novel_name': novel_name,
                'author': author,
                'novel_characters': novel_characters,
                'update_time': update_time_int,
                'novel_status': novel_status,
                'url': novel_url
            }
            print(novel)
            # 将数据写入数据库
            self.mysql_operator.add('novels', novel)
            # 进一步请求这本小说的主页，获取章节列表
            self.download_and_parse_novel_page(novel_url, novel_id)
            # break

    def run(self):
        """
        爬虫运行入口
        :return:
        """
        # 逐页面地对列表页进行处理
        for page in range(1, self.total_page + 1):
            self.download_and_parse_list_page(page)
        # 关闭数据库操作器
        self.mysql_operator.close()


if __name__ == '__main__':
    X23usSpider().run()
