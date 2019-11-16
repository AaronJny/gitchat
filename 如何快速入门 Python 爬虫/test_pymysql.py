# -*- coding: utf-8 -*-
# @File    : test_pymysql.py
# @Author  : AaronJny
# @Date    : 2019/11/13
# @Desc    : 通过pymysql演示数据库基本的增删该查操作
import pymysql


def create_conn(db='mysql'):
    """
    创建一个指定db的数据库连接
    :param db:数据库名
    :return:
    """
    conn = pymysql.connect(host="localhost", port=3306, user='root', password='123456', db=db)
    return conn


def test_insert():
    """
    插入操作
    :return:
    """
    sql = """
    insert into spider.test_table(name, age) values (%s,%s)
    """
    # 待插入的数据列表
    records = [('张三', 21), ('李四', 22), ('王二', 23), ('麻子', 24)]
    # 创建数据库连接
    conn = create_conn(db='spider')
    # 插入数据
    cursor = conn.cursor()
    cursor.executemany(sql, records)
    cursor.close()
    # 提交
    conn.commit()
    # 关闭数据库连接
    conn.close()


def test_update():
    """
    更新操作
    :return:
    """
    sql = """
    update spider.test_table set age=30 where name='张三'
    """
    # 创建数据库连接
    conn = create_conn(db='spider')
    # 执行更新
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    # 提交
    conn.commit()
    # 关闭数据库连接
    conn.close()


def test_delete():
    """
    删除操作
    :return:
    """
    sql = """
    delete from spider.test_table where age=23
    """
    # 创建数据库连接
    conn = create_conn(db='spider')
    # 执行删除操作
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    # 提交
    conn.commit()
    # 关闭数据库连接
    conn.close()


def test_select():
    """
    查询操作
    :return:
    """
    sql = """
    select * from spider.test_table
    """
    # 创建数据库连接
    conn = create_conn(db='spider')
    # 执行删除操作
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    res = cursor.fetchall()
    cursor.close()
    # 关闭数据库连接
    conn.close()
    # 输出查询结果
    print(res)


if __name__ == '__main__':
    test_select()
