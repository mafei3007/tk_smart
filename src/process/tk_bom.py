# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-30 10:27
@Desc   ：BOM管理
==================================================
"""
import datetime

from db.comm_cnn import CommonCnn
from tk_util import write_log, free_obj
from constant import default_pwd


# 查询人员列表信息
def get_em_list(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    em_id = js.get('id', None)
    em_name = js.get('name', None)
    em_code = js.get('code', None)
    status = js.get('status', '有效')
    duty = js.get('duty', None)
    start_dt = js.get('start_dt', None)
    end_dt = js.get('end_dt', None)
    page_no = js.get('page_no', 0)
    page_size = js.get('page_size', 0)
    order_field = js.get('order_field', 'id')
    order = js.get('order', 'asc')
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        e_args = []
        str_count = 'select count(*) from t_em where status=%s'
        str_sql = 'select * from t_em where status=%s'
        e_args.append(status)
        if em_id:
            str_sql = str_sql + ' and id=%s'
            str_count = str_count + ' and id=%s'
            e_args.append(em_id)
        if em_name:
            str_sql = str_sql + ' and name=%s'
            str_count = str_count + ' and name=%s'
            e_args.append(em_name)
        if em_code:
            str_sql = str_sql + ' and code=%s'
            str_count = str_count + ' and code=%s'
            e_args.append(em_code)
        if em_code:
            str_sql = str_sql + ' and code=%s'
            str_count = str_count + ' and code=%s'
            e_args.append(em_code)
        if duty:
            str_sql = str_sql + ' and duty=%s'
            str_count = str_count + ' and duty=%s'
            e_args.append(duty)
        if start_dt:
            str_sql = str_sql + ' and dt>=%s'
            str_count = str_count + ' and dt>=%s'
            e_args.append(start_dt)
        if end_dt:
            str_sql = str_sql + ' and dt<=%s'
            str_count = str_count + ' and dt<=%s'
            e_args.append(end_dt)
        cur.execute(str_count, args=e_args)
        r = cur.fetchone()
        js_ret['len'] = r[0]
        str_sql = str_sql + ' order by ' + order_field + ' ' + order
        if page_no > 0 and page_size > 0:  # 如果分页
            str_sql = str_sql + ' limit ' + str((page_no - 1) * page_size) + ',' + str(page_size)
        if e_args:
            str_msg = '查询SQL:%s,参数:%s' % (str_sql, e_args)
        else:
            str_msg = '查询SQL:%s,参数:空' % str_sql
        write_log(str_msg, tenant=tenant)
        cur.execute(str_sql, args=e_args)
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


# 添加人员
def add_em(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    name = js['name']
    code = js['code']
    duty = js['duty']
    email = js.get('email', '')
    phone = js.get('phone', '')
    password = js.get('password', default_pwd)
    addr = js.get('addr', '')
    status = js.get('status', '有效')
    remark = js.get('remark', '')
    lst_rl = js.get('role', [])
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_em where name=%s or code=%s'
        cur.execute(str_sql, args=[name, code])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '姓名%s或代号%s已经存在，不能重复添加' % (name, code)
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_em(code,name,duty,phone,email,password,addr,status,remark) values' \
                  '(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(str_sql, args=[code, name, duty, phone, email, password, addr, status, remark])
        str_sql = 'select id from t_em where name=%s and code=%s'
        cur.execute(str_sql, args=[name, code])
        r = cur.fetchone()
        em_id = r[0]
        for rl_id in lst_rl:
            str_sql = 'insert into t_em_role(em_id,rl_id) values(%s,%s)'
            cur.execute(str_sql, args=[em_id, rl_id])
        str_msg = '添加人员：姓名%s,代号%s' % (name, code)
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改人员
def edit_em(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    em_id = js['id']
    name = js.get('name', None)
    code = js.get('code', None)
    duty = js.get('duty', None)
    email = js.get('email', None)
    phone = js.get('phone', None)
    password = js.get('password', None)
    addr = js.get('addr', None)
    status = js.get('status', None)
    remark = js.get('remark', '')
    lst_rl = js.get('role', None)
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_em where id=%s'
        cur.execute(str_sql, args=[em_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '人员信息%s不存在，无法删除' % em_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_em where (name=%s or code=%s) and id!=%s'
        cur.execute(str_sql, args=[name, code, em_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '姓名%s或代号%s重复' % (name, code)
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'update t_em set remark=%s'
        e_args = [remark]
        if code:
            str_sql = str_sql + ',code=%s'
            e_args.append(code)
        if name:
            str_sql = str_sql + ',name=%s'
            e_args.append(name)
        if duty:
            str_sql = str_sql + ',duty=%s'
            e_args.append(duty)
        if phone:
            str_sql = str_sql + ',phone=%s'
            e_args.append(phone)
        if email:
            str_sql = str_sql + ',email=%s'
            e_args.append(email)
        if password:
            str_sql = str_sql + ',password=%s'
            e_args.append(password)
        if addr:
            str_sql = str_sql + ',addr=%s'
            e_args.append(addr)
        if status:
            str_sql = str_sql + ',status=%s'
            e_args.append(status)
        str_sql = str_sql + ' where id=%s'
        e_args.append(em_id)
        cur.execute(str_sql, args=e_args)
        if lst_rl:
            str_sql = 'delete from t_em_role where em_id=%s'
            cur.execute(str_sql, args=[em_id])
            for rl_id in lst_rl:
                str_sql = 'insert into t_em_role(em_id,rl_id) values(%s,%s)'
                cur.execute(str_sql, args=[em_id, rl_id])
        str_msg = '更新人员信息%s' % em_id
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 删除人员
def del_em(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    em_id = js['id']
    force = js.get('force', False)
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_em where id=%s'
        cur.execute(str_sql, args=[em_id])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s不存在' % em_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'delete from t_em_role where id=%s'
        cur.execute(str_sql, args=[em_id])
        if force:
            str_sql = 'delete from t_em where id=%s'
            cur.execute(str_sql, args=[em_id])
        else:
            str_sql = 'update t_em set status=%s where id=%s'
            cur.execute(str_sql, args=['失效', em_id])
        str_msg = '删除人员信息%s' % em_id
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    js = {'tenant': 'tk_huawei', 'id': 1, 'em_id': 1, 'opt_id': 1}
    print(del_em(js))


if __name__ == '__main__':
    main()
