# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-28 08:36
@Desc   ：仓库基本信息
==================================================
"""
import datetime
import json

from tk_util import write_log
from process.srv_util import get_tenant_cnn, free_obj


# 查询仓库信息
def get_stock(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    order_field = js.get('order_field', 'id')
    order = js.get('order', 'asc')
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        qry_args = []
        str_sql = 'select * from t_stock'
        str_sql = str_sql + ' order by ' + order_field + ' ' + order
        if qry_args:
            str_msg = '查询SQL:%s,参数:%s' % (str_sql, qry_args)
        else:
            str_msg = '查询SQL:%s,参数:空' % str_sql
        write_log(str_msg, tenant=tenant)
        cur.execute(str_sql, args=qry_args)
        rr = cur.fetchall()
        js_ret['len'] = len(rr)
        for r in rr:
            lst_r = list()
            for o in r:
                if isinstance(o, datetime.datetime):  # 对于日期时间需要特殊处理一下，否则dumps会报错 马飞 202203271136
                    lst_r.append(o.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    lst_r.append(o)
            js_ret['data'].append(lst_r)
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 添加仓库
def add_stock(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    name = js['name']
    remark = js.get('remark', '')
    is_default = js.get('is_default', 0)
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_stock where name=%s'
        cur.execute(str_sql, args=[name])
        r = cur.fetchone()
        if r[0] > 0:  # 该仓库已经存在
            str_msg = '%s已经存在，不能重复添加' % name
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_stock(name,is_default,remark) values(%s,%s,%s)'
        cur.execute(str_sql, args=[name, is_default, remark])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改仓库
def edit_stock(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    stock_id = js['stock_id']
    name = js.get('name', '')
    is_default = js.get('is_default', -1)
    remark = js.get('remark', '')
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'update t_stock set remark=%s'
        e_args = [remark]
        if name != '':
            str_sql = str_sql + ',name=%s'
            e_args.append(name)
        if is_default != -1:
            str_sql = str_sql + ',is_default=%s'
            e_args.append(is_default)
        str_sql = str_sql + ' where id=%s'
        e_args.append(stock_id)
        cur.execute(str_sql, args=e_args)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 删除
def del_stock(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    stock_id = js['stock_id']
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_stock where id=%s'
        cur.execute(str_sql, args=[stock_id])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s不存在' % stock_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_good where stock_id=%s'
        cur.execute(str_sql, args=[stock_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s已经被产品引用，无法删除' % stock_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret

        str_sql = 'select count(*) from t_checkin where stock_id=%s'
        cur.execute(str_sql, args=[stock_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s已经被物料入库记录引用，无法删除' % stock_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_checkout where stock_id=%s'
        cur.execute(str_sql, args=[stock_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s已经被物料出库记录引用，无法删除' % stock_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'delete from t_stock where id=%s'
        cur.execute(str_sql, args=[stock_id])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    js = {'tenant': 'tk_huawei', 'stock_id': 11}
    js_ret = json.dumps(get_stock(js), ensure_ascii=False)
    print(js_ret)


if __name__ == '__main__':
    main()
