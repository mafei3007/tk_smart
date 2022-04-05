# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-30 22:20
@Desc   ：生产工单管理
==================================================
"""
import datetime
import threading
import time

from tk_util import write_log, free_obj
from db.comm_cnn import CommonCnn
from process.tk_config import get_idx
from constant import prod_idx

lock = threading.Lock()


def get_prod_plan_name(tenant):
    lock.acquire()
    try:
        prod_plan_name = prod_idx + '_' + time.strftime('%Y%m%d', time.localtime(time.time())) + \
                         '_%d' % get_idx(tenant, prod_idx)
        str_msg = '获取生产工单名称%s' % prod_plan_name
        write_log(str_msg, tenant=tenant)
        return prod_plan_name
    finally:
        lock.release()


def main():
    js = {'tenant': 'tk_huawei'}
    print(js)


if __name__ == '__main__':
    main()
