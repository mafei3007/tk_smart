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
    base_cnn = None
    cnn_pool = None

    def __init__(self):
        if not self.base_cnn:
            self.base_cnn = PooledDB(
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
                charset=comm_db_charset,
                setsession=['SET AUTOCOMMIT = 1']
            )
        if not self.cnn_pool:
            self.cnn_pool = dict()
            cnn = self.base_cnn.connection()
            str_sql = 'select tenant_code,db_host,db_user,db_pwd,db_name,db_charset,status,max_cnn from t_tenant'
            cur = cnn.cursor()
            cur.execute(str_sql)
            rr = cur.fetchall()
            for r in rr:
                tenant = r[0]
                db_host = r[1]
                db_user = r[2]
                db_pwd = r[3]
                db_name = r[4]
                db_charset = r[5]
                status = r[6]
                max_cnn = r[7]
                if status != '有效':
                    continue
                try:
                    self.cnn_pool[tenant] = PooledDB(
                        # 使用链接数据库的模块
                        creator=pymysql,
                        # 连接池允许的最大连接数，0和None表示不限制连接数
                        maxconnections=max_cnn,
                        # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                        mincached=1,
                        # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
                        blocking=True,
                        # 一个链接最多被重复使用的次数，None表示无限制
                        maxusage=None,
                        # 主机地址
                        host=db_host,
                        # 端口
                        port=3306,
                        # 数据库用户名
                        user=db_user,
                        # 数据库密码
                        password=db_pwd,
                        # 数据库名
                        database=db_name,
                        # 字符编码
                        charset=db_charset,
                        setsession=['SET AUTOCOMMIT = 1']
                    )
                except Exception as e:
                    print(e)
            cur.close()
            cnn.close()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                cls._instance = super().__new__(cls)
        return cls._instance


def main():
    conn = CommonCnn().base_cnn.connection()
    # 创建游标
    cursor = conn.cursor()
    # SQL语句
    str_sql = 'select city_name from t_city where instr(city_name,%s)'
    cursor.execute(str_sql, args=['山'])
    # 执行结果
    result = cursor.fetchall()
    print(result)
    # 将conn释放,放回连接池
    conn.close()

    conn_1 = CommonCnn().cnn_pool['tk_huawei'].connection()
    # 创建游标
    cursor = conn_1.cursor()
    # SQL语句
    str_sql = 'select code from t_em where id=%s'
    cursor.execute(str_sql, args=[22])
    r = cursor.fetchone()
    print(r)
    # 将conn释放,放回连接池
    conn_1.close()


if __name__ == '__main__':
    main()
