# -*- coding: UTF-8 -*-
"""
=================================================
@Project ：tk_smart
@Author ：Ma fei
@Date   ：2022-04-04 13:12
@Desc   ：扩展属性实例明细管理
==================================================
"""

import datetime
from tk_util import write_log, free_obj, is_none
from db.comm_cnn import CommonCnn


# 查询
def get_ext_inst_list(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    ext_id = js.get('ext_id', None)
    page_no = js.get('page_no', 0)
    page_size = js.get('page_size', 0)
    order_field = js.get('order_field', 'id')
    order = js.get('order', 'asc')
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        qry_args = []
        str_count = 'select count(a.id) from t_ext_inst as a,t_ext as b where a.ext_id=b.id'
        str_sql = 'select a.id,a.value,a.remark,b.id as ext_id, b.code as ext_code from t_ext_inst as a,' \
                  't_ext as b where a.ext_id=b.id'
        if ext_id:
            str_sql = str_sql + ' and b.id=%s'
            str_count = str_count + ' and b.id=%s'
            qry_args.append(ext_id)
        cur.execute(str_count, args=qry_args)
        r = cur.fetchone()
        js_ret['len'] = r[0]
        str_sql = str_sql + ' order by ' + order_field + ' ' + order
        if page_no > 0 and page_size > 0:  # 如果分页
            str_sql = str_sql + ' limit ' + str((page_no - 1) * page_size) + ',' + str(page_size)
        if qry_args:
            str_msg = '查询SQL:%s,参数:%s' % (str_sql, qry_args)
        else:
            str_msg = '查询SQL:%s,参数:空' % str_sql
        write_log(str_msg, tenant=tenant)
        cur.execute(str_sql, args=qry_args)
        rr = cur.fetchall()
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


# 添加
def add_ext_inst(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    ext_id = js.get('ext_id', None)
    ext_code = js.get('ext_code', None)
    value = js.get('value', None)
    remark = js.get('remark', '')
    if ext_id is None and ext_code is None:
        str_msg = '扩展属性ID和代号不能都为空'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    if value is None:
        str_msg = '扩展属性实例的值螚为空'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        q_args = []
        str_sql = 'select id,code from t_ext where 1=1'
        if ext_id:
            str_sql = str_sql + ' and id=%s'
            q_args.append(ext_id)
        if ext_code:
            str_sql = str_sql + ' and code=%s'
            q_args.append(ext_code)
        cur.execute(str_sql, args=[ext_id, value])
        r = cur.fetchone()
        if r is None:
            str_msg = '扩展属性不存在，无法增加该扩展属性实例'
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        ext_id = r[0]
        ext_code = r[1]
        str_sql = 'select count(*) from t_ext_inst where ext_id=%s and value=%s'
        cur.execute(str_sql, args=[ext_id, value])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '扩展属性%s，值为%s的实例已经存在，不能重复添加' % (ext_code, value)
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_ext_inst(ext_id,value,remark) values(%s,%s,%s)'
        cur.execute(str_sql, args=[ext_id, value, remark])
        str_msg = '添加扩展属性%s的实例%s' % (ext_code, value)
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改
def edit_ext_inst(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    ext_inst_id = js['id']
    ext_id = js.get('ext_id', None)
    value = js.get('value', None)
    remark = js.get('remark', None)
    if is_none([ext_id, value, remark]):
        str_msg = '没有需要更新扩展属性实例信息' % ext_id
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_ext_inst where id=%s'
        cur.execute(str_sql, args=[ext_inst_id])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '扩展属性实例%s不存在，无法更新' % ext_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        if ext_id:
            str_sql = 'select count(*) from t_ext where id=%s'
            cur.execute(str_sql, args=[ext_id])
            r = cur.fetchone()
            if r[0] > 0:
                str_msg = '扩展属性不存在，无法更新' % ext_id
                js_ret['err_msg'] = str_msg
                write_log(str_msg, tenant=tenant)
                return js_ret
        str_sql = 'update t_ext_inst set '
        e_args = []
        if ext_id:
            str_sql = str_sql + ',ext_id=%s'
            e_args.append(ext_id)
        if value:
            str_sql = str_sql + ',value=%s'
            e_args.append(value)
        if remark:
            str_sql = str_sql + ',remark=%s'
            e_args.append(remark)
        str_sql = str_sql + ' where id=%s'
        e_args.append(ext_inst_id)
        cur.execute(str_sql, args=e_args)
        str_msg = '更新扩展属性实例信息%s成功' % ext_inst_id
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 删除
def del_ext_inst(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    ext_inst_id = js['id']
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select id from t_ext_inst where id=%s'
        cur.execute(str_sql, args=[ext_inst_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '%s不存在,删除失败' % ext_inst_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_ext_detail where ext_inst_id=%s'
        cur.execute(str_sql, args=[ext_inst_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s被物料引用了，无法删除' % ext_inst_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'delete from t_ext_inst where id=%s'
        cur.execute(str_sql, args=[ext_inst_id])
        str_msg = '删除扩展属性实例信息%s成功' % ext_inst_id
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    js = {'tenant': 'tk_huawei', 'code': 'sss', 'opt_id': 1}
    print(del_ext_inst(js))


if __name__ == '__main__':
    main()
