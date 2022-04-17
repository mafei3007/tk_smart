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


def process_add_em(prefix_name, prefix_code, n_count):
    t_start = time.time()
    for i in range(1, n_count):
        name = '卡尔.%s_%d' % (prefix_name, i)
        code = '卡尔.%s_%d' % (prefix_code, i)
        js = {'tenant': 'tk_huawei', 'opt_id': 1, 'name': name, 'code': code, 'duty': '掌门',
              'email': 'zhangsanfeng@wudang.com', 'phone': '13899998888', 'password': 'Fh@123.com', 'remark': '武当派创始人',
              'addr': '武当山'}
        add_em(js)
    g_th_queue.get_nowait()
    avg_value = 1000 * (time.time() - t_start) / n_count
    str_msg = '姓名前缀%10s,代号前缀%10s,共%d条记录,每条记录耗时%5.2f毫秒' % (prefix_name, prefix_code, n_count, avg_value)
    print(str_msg)


def main():
    th_count = 20
    m_count = 100
    m_start = time.time()
    for i in range(1, th_count):
        g_th_queue.put_nowait(i)
        prefix_name = '姓名_%d' % i
        prefix_code = 'code_%d' % i
        _thread.start_new_thread(process_add_em, (prefix_name, prefix_code, m_count))
    while g_th_queue.qsize() > 0:
        time.sleep(1)
    elapsed_ms = (time.time() - m_start)
    m_msg = '所有数据已经预置完成,耗时%.2f秒' % elapsed_ms
    print(m_msg)


if __name__ == '__main__':
    # 这是一个样例
    main()
