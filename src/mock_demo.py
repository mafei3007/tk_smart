# -*- coding: UTF-8 -*-
"""
=================================================
@Project ：tk_smart
@Author ：Ma fei
@Date   ：2022-04-15 20:58
@Desc   ：
==================================================
"""
import _thread
import re
import time
from queue import Queue

from process.tk_em import add_em

g_th_queue = Queue()


def process_add_em(prefix_name, prefix_code):
    for i in range(1, 1000):
        name = '卡尔.%s_%d' % (prefix_name, i)
        code = '卡尔.%s_%d' % (prefix_code, i)
        js = {'tenant': 'tk_huawei', 'opt_id': 1, 'name': name, 'code': code, 'duty': '掌门',
              'email': 'zhangsanfeng@wudang.com', 'phone': '13899998888', 'password': 'Fh@123.com', 'remark': '武当派创始人',
              'addr': '武当山'}
        add_em(js)
    g_th_queue.get_nowait()
    print(prefix_name, prefix_code, '完成了')


def main():
    for i in range(1, 20):
        g_th_queue.put_nowait(i)
        prefix_name = '姓名_%d' % i
        prefix_code = 'code_%d' % i
        _thread.start_new_thread(process_add_em, (prefix_name, prefix_code))
        print('==========', i)


if __name__ == '__main__':
    t1 = time.time()
    main()
    while g_th_queue.qsize() > 0:
        time.sleep(10)
    print('所有数据已经预置完成', time.time() - t1)
