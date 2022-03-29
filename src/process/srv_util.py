# -*- coding: UTF-8 -*-


"""
=================================================
@Project -> File   ：tk_smart -> srv_util
@Author ：Ma fei
@Date   ：2022-03-23 10:53
@Desc   ：
==================================================
"""
import datetime
import json
import uuid
import base64
import pymysql
import os
import time
import qrcode
from pathlib import Path
from src.tk_util import write_log, deal_db_err
from db.comm_cnn import CommonCnn

g_tenant = 'tk_huawei'


def get_bc_img(bc_content):
    # version参数----二维码的格子矩阵大小，可以是1到40，1最小为21*21，40是177*177
    # error_correction参数----二维码错误容许率，默认ERROR_CORRECT_M，容许小于15%的错误率
    # box_size参数----二维码每个小格子包含的像素数量
    # border参数----二维码到图片边框的小格子数，默认值为4
    img_res = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'img_res'
    if not Path(img_res).exists():
        os.mkdir(img_res)
    img_file = time.strftime('%Y%m%d%H%M%S_', time.localtime(time.time())) + str(uuid.uuid4()) + '.bmp'
    img_file = img_res + os.sep + img_file
    if os.path.exists(img_file):
        os.remove(img_file)
    img = qrcode.make(bc_content, version=4, box_size=20, border=2)
    img.save(img_file)
    return img_file


# 加密 解密
def get_pwd(s, encode=True):
    if encode:  # 加密
        s = s + '*13dc%'
        str_ret = base64.b64encode(s.encode())
    else:  # 解密
        str_ret = base64.b64decode(s).decode()
        str_ret = str_ret[:-6]
    return str_ret


def free_obj(obj):
    if obj is None:
        return
    try:
        obj.close()
    except Exception as em:
        str_err = '释放对象异常:%s' % repr(em).split('(')[0]
        write_log(str_err)


def get_tenant_cnn(tenant):
    cnn = CommonCnn().cnn_pool.connection()
    try:
        str_sql = 'select db_host,db_user,db_pwd,db_name,db_charset from t_tenant where tenant_code=%s'
        cur = cnn.cursor()
        cur.execute(str_sql, args=[tenant])
        r = cur.fetchone()
        cur.close()
    finally:
        cnn.close()
    cnn = pymysql.connect(host=r[0], user=r[1], password=r[2], database=r[3], charset=r[4], autocommit=True)
    return cnn


def exec_sql(str_sql, args=None, tenant=None):
    if args:
        str_msg = '更新SQL:%s,参数:%s' % (str_sql, args)
    else:
        str_msg = '更新SQL:%s,参数:空' % str_sql
    write_log(str_msg)
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        effected_rows = cur.execute(str_sql, args=args)
        if effected_rows > 0:
            cnn.commit()
        return effected_rows, True
    except Exception as em:
        str_msg = deal_db_err(em, str_sql, args)
        write_log(str_msg, tenant=tenant)
        return -1, False
    finally:
        free_obj(cur)
        free_obj(cnn)


def qry_sql(str_sql, args=None, tenant=None):
    if args:
        str_msg = '更新SQL:%s,参数:%s' % (str_sql, args)
    else:
        str_msg = '更新SQL:%s,参数:空' % str_sql
    write_log(str_msg, tenant=tenant)
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        cur.execute(str_sql, args=args)
        rr = cur.fetchall()
        return rr, True
    except Exception as em:
        str_msg = deal_db_err(em, str_sql, args)
        write_log(str_msg, tenant=tenant)
        return None, False
    finally:
        free_obj(cur)
        free_obj(cnn)


def get_tb_data(cond):
    js_param = cond.copy()
    page_no = js_param.get('page_no', 0)
    page_size = js_param.get('page_size', 0)
    order_field = js_param.get('order_field', 'id')
    order = js_param.get('order', 'asc')
    tenant = js_param.get('tenant', g_tenant)
    start_dt = js_param.get('start_dt', None)
    end_dt = js_param.get('end_dt', None)
    tb_name = js_param.get('tb_name', 't_unit')
    if 'page_no' in js_param.keys():
        del js_param['page_no']
    if 'page_size' in js_param.keys():
        del js_param['page_size']
    if 'order_field' in js_param.keys():
        del js_param['order_field']
    if 'order' in js_param.keys():
        del js_param['order']
    if 'tb_name' in js_param.keys():
        del js_param['tb_name']
    if 'tenant' in js_param.keys():
        del js_param['tenant']
    if 'start_dt' in js_param.keys():
        del js_param['start_dt']
    if 'end_dt' in js_param.keys():
        del js_param['end_dt']
    str_count = 'select count(*) from ' + tb_name + ' where 1=1 '
    str_sql = 'select * from ' + tb_name + ' where 1=1 '
    qry_args = list()
    if start_dt:
        qry_args.append(start_dt)
        str_count = str_count + 'and dt>%s '
        str_sql = str_sql + 'and dt>%s '
    if end_dt:
        qry_args.append(end_dt)
        str_count = str_count + 'and dt<%s '
        str_sql = str_sql + 'and dt<%s '
    for k in js_param.keys():  # 非时间字段
        qry_args.append(js_param.get(k))
        str_count = str_count + 'and ' + k + '=%s '
        str_sql = str_sql + 'and ' + k + '=%s '
    str_sql = str_sql + ' order by ' + order_field + ' ' + order + ' '
    if page_no > 0 and page_size > 0:
        str_sql = str_sql + ' limit ' + str((page_no - 1) * page_size) + ',' + str(page_size)
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['data'] = None
    js_ret['len'] = -1
    if qry_args:
        str_msg = '查询SQL:%s,参数:%s' % (str_sql, qry_args)
    else:
        str_msg = '查询SQL:%s,参数:空' % str_sql
    write_log(str_msg)
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        cur.execute(str_count, args=qry_args)
        r = cur.fetchone()
        rec_size = r[0]
        cur.execute(str_sql, args=qry_args)
        rr = cur.fetchall()
    except Exception as em:
        str_msg = deal_db_err(em, str_sql, qry_args)
        write_log(str_msg, tenant=tenant)
        js_ret['err_msg'] = str_msg
        return js_ret
    finally:
        free_obj(cur)
        free_obj(cnn)
        write_log(str_msg, tenant=tenant)
    lst_data = list()
    for r in rr:
        lst_r = list()
        for o in r:
            if isinstance(o, datetime.datetime):  # 对于日期时间需要特殊处理一下，否则dumps会报错 马飞 202203271136
                lst_r.append(o.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                lst_r.append(o)
        lst_data.append(lst_r)
    js_ret['len'] = rec_size
    js_ret['data'] = lst_data
    return js_ret


def main():
    qry_cond = {'op_content': '登录系统', 'em_id': 77, 'tb_name': 't_logs', 'page_no': 1, 'page_size': 10,
                'start_dt': '2020-07-01 00:00:00', 'end_dt': '2020-08-30 00:00:00'}
    js_ret = get_tb_data(qry_cond)
    str_ret = json.dumps(js_ret, ensure_ascii=False)
    print(str_ret)


if __name__ == '__main__':
    main()
