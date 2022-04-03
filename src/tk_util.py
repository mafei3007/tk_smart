# -*-coding:utf-8-*-

"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-23 10:53
@Desc   ：
==================================================
"""

import json
import socket
import traceback
import httplib2
import os
import time
from pathlib import Path
from db.comm_cnn import CommonCnn


def get_host():
    my_name = socket.getfqdn(socket.gethostname())
    my_address = socket.gethostbyname(my_name)
    return my_address


def get_curr():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def free_obj(obj):
    if obj is None:
        return
    try:
        obj.close()
    except Exception as em:
        str_err = '释放对象异常:%s' % repr(em).split('(')[0]
        write_log(str_err)


def deal_db_err(em, str_sql, args):
    em_name = repr(em).split('(')[0]
    if args:
        err_msg = 'SQL:%s,参数%s,异常：%s，详细异常：%s' % (str_sql, str(args), em_name, traceback.format_exc())
    else:
        err_msg = 'SQL:%s,参数空,异常：%s，详细异常：%s' % (str_sql, em_name, traceback.format_exc())
    write_log(err_msg)
    return err_msg


def qry_common_sql(str_sql, args=None):
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool.connection()
        cur = cnn.cursor()
        cur.execute(str_sql, args=args)
        rr = cur.fetchall()
        return rr, None
    except Exception as em:
        return None, deal_db_err(em, str_sql, args)
    finally:
        free_obj(cur)
        cnn.close()


def exec_common_sql(str_sql, args=None):
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool.connection()
        cur = cnn.cursor()
        effected_rows = cur.execute(str_sql, args=args)
        if effected_rows > 0:
            cnn.commit()
        return effected_rows, None
    except Exception as em:
        return -1, deal_db_err(em, str_sql, args)
    finally:
        free_obj(cur)
        cnn.close()


def send_message(url, method='GET', js_body=None, js_header=None):
    status = 404
    js_resp = dict()
    if js_header:
        js_header = {'Content-type': 'application/json'}
    try:
        http_obj = httplib2.Http(timeout=30)  # 默认超时30秒
        response, content = http_obj.request(url, method=method, headers=js_header,
                                             body=json.dumps(js_body, ensure_ascii=True))
        status = response.status
        js_resp = json.loads(content)
        print(json.dumps(js_resp, indent=4))
    except Exception as em:
        err_msg = '%s,详细异常:%s.' % (repr(em), traceback.format_exc())
        js_resp['err_msg'] = err_msg
    return status, js_resp


def write_log(str_msg, tenant=None):
    # dir_log = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'logs'
    dir_log = r'D:\py_workspace\tk_smart\logs'
    if not Path(dir_log).exists():
        os.mkdir(dir_log)
    if tenant:
        log_file = dir_log + os.sep + time.strftime('%Y%m%d', time.localtime(time.time())) + '_' + tenant + '.log'
    else:
        log_file = dir_log + os.sep + time.strftime('%Y%m%d', time.localtime(time.time())) + '.log'
    str_log = '%s %s\n' % (get_curr(), str_msg)
    try:
        with open(log_file, 'a', encoding='utf8') as f:
            f.write(str_log)
    except Exception as em:
        str_err = '%s,详细异常:%s.' % (repr(em), traceback.format_exc())
        print(str_err)


def free_obj(obj):
    if obj is None:
        return
    try:
        obj.close()
    except Exception as em:
        str_err = '释放对象异常:%s' % repr(em).split('(')[0]
        write_log(str_err)


def main():
    # str_sql = 'select * from t_city'
    # t1 = time.time()
    # for i in range(1, 10):
    #     print(qry_common_sql(str_sql))
    # print(time.time() - t1)
    # s_sql = "insert into t_tenant (tenant_code, company, contact, phone, telephone, addr, " \
    #         "email, reg_dt, reg_code) values('tk_huawei', '南京华为', '马飞', '13951623007', '025-8336666', " \
    #         "'软件大道101号', 'huawei@huawei.com', '2022-03-21 09:44:17', null);"
    # print(exec_sql(s_sql))
    url = 'http://192.168.1.5:5005/login'
    method = 'GET'
    js_bd = {'user': '马飞', 'code': 'hero'}
    js_hd = {'user-id': 'mafei', 'tenant_id': 'tk_huawei'}
    print(send_message(url, method=method, js_body=js_bd, js_header=js_hd))
    # bc_content = 'this is a test message'
    # print(get_bc_img(bc_content))
    # print(get_express_info(''))


if __name__ == '__main__':
    main()
