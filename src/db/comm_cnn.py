# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-27 19:40
@Desc   ：公共数据库连接管理类
==================================================
"""

import threading

import pymysql
from dbutils.pooled_db import PooledDB  # 安装DbUtils插件
from constant import comm_db_host, comm_db_user, comm_db_name, comm_db_pwd, comm_db_charset


class CommonCnn(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        self.cnn_pool = PooledDB(
            # 使用链接数据库的模块
            creator=pymysql,
            # 连接池允许的最大连接数，0和None表示不限制连接数
            maxconnections=10,
            # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            mincached=5,
            # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            blocking=True,
            # 一个链接最多被重复使用的次数，None表示无限制
            maxusage=None,
            # 主机地址
            host=comm_db_host,
            # 端口
            port=3306,
            # 数据库用户名
            user=comm_db_user,
            # 数据库密码
            password=comm_db_pwd,
            # 数据库名
            database=comm_db_name,
            # 字符编码
            charset=comm_db_charset
        )

    def __new__(cls, *args, **kwargs):
        if not hasattr(CommonCnn, "_instance"):
            with CommonCnn._instance_lock:
                if not hasattr(CommonCnn, "_instance"):
                    # 类加括号就回去执行__new__方法，__new__方法会创建一个类实例：CommonCnn()
                    CommonCnn._instance = object.__new__(cls)  # 继承object类的__new__方法，类去调用方法，说明是函数，要手动传cls
        return CommonCnn._instance  # obj1
        # 类加括号就会先去执行__new__方法，在执行__init__方法


def main():
    conn = CommonCnn().cnn_pool.connection()
    # 创建游标
    cursor = conn.cursor()
    # SQL语句
    cursor.execute('select * from t_city')
    # 执行结果
    result = cursor.fetchall()
    print(len(result))
    # 将conn释放,放回连接池
    conn.close()

    conn_1 = CommonCnn().cnn_pool.connection()
    # 创建游标
    cursor = conn_1.cursor()
    # SQL语句
    cursor.execute('select * from t_city')
    # 执行结果
    result = cursor.fetchall()
    print(len(result))
    # 将conn释放,放回连接池
    conn_1.close()


if __name__ == '__main__':
    main()