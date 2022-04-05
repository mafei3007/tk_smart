# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-28 08:36
@Desc   ：出入库管理
==================================================
"""
import datetime
import threading
import time

from tk_util import write_log, free_obj
from process.tk_config import get_idx
from db.comm_cnn import CommonCnn


def main():
    js = {'tenant': 'tk_huawei'}
    print(js)


if __name__ == '__main__':
    main()
