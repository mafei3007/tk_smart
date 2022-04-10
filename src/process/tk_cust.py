# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-30 10:27
@Desc   ：客户信息管理
==================================================
"""
import datetime
from tk_util import write_log, free_obj, is_none
from db.comm_cnn import CommonCnn


# 查询信息
def get_cust_list(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    cust_id = js.get('id', None)
    name = js.get('name', None)
    code = js.get('code', None)
    status = js.get('status', None)
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
        qry_args = []
        str_count = 'select count(id) from t_cust where 1=1'
        str_sql = 'select id,name,code,status,bank,account,credit_code,address,contact,phone,email,status,' \
                  'remark from t_cust where 1=1'
        if cust_id:
            str_sql = str_sql + ' and id=%s'
            str_count = str_count + ' and id=%s'
            qry_args.append(cust_id)
        if name:
            str_sql = str_sql + ' and name=%s'
            str_count = str_count + ' and name=%s'
            qry_args.append(name)
        if code:
            str_sql = str_sql + ' and code=%s'
            str_count = str_count + ' and code=%s'
            qry_args.append(code)
        if status:
            str_sql = str_sql + ' and status=%s'
            str_count = str_count + ' and status=%s'
            qry_args.append(status)
        if start_dt:
            str_sql = str_sql + ' and dt>=%s'
            str_count = str_count + ' and dt>=%s'
            qry_args.append(start_dt)
        if end_dt:
            str_sql = str_sql + ' and dt<=%s'
            str_count = str_count + ' and dt<=%s'
            qry_args.append(end_dt)
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
def add_cust(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    name = js['name']
    code = js['code']
    bank = js['bank']
    account = js['account']
    credit_code = js['credit_code']
    address = js['address']
    contact = js['contact']
    phone = js.get('phone', '')
    email = js.get('email', '')
    status = js.get('status', '有效')
    remark = js.get('remark', '')
    if status not in ['有效', '无效']:
        str_msg = '状态必须是\"有效\"或者\"无效\"'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_cust where name=%s or code=%s'
        cur.execute(str_sql, args=[name, code])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '名称%s或代号%s已经存在，不能重复添加' % (name, code)
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_cust(name,code,status,bank,account,credit_code,address,contact,phone,email,' \
                  'status,remark) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(str_sql,
                    args=[name, code, status, bank, account, credit_code, address, contact, phone, email, status,
                          remark])
        str_msg = '添加客户：名称%s,代号%s' % (name, code)
        str_sql = 'insert into t_logs(cust_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改
def edit_cust(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    cust_id = js['id']
    name = js.get('name', None)
    code = js.get('code', None)
    bank = js.get('bank', None)
    account = js.get('account', None)
    credit_code = js.get('credit_code', None)
    address = js.get('address', None)
    contact = js.get('contact', None)
    phone = js.get('phone', None)
    email = js.get('email', None)
    status = js.get('status', None)
    remark = js.get('remark', '')
    if status:
        if status not in ['有效', '无效']:
            str_msg = '状态必须是\"有效\"或者\"无效\"'
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
    if is_none([name, code, bank, account, credit_code, address, contact, phone, email, status, remark]):
        str_msg = '没有需要更新的信息'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_cust where id=%s'
        cur.execute(str_sql, args=[cust_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '客户信息%s不存在，无法更新' % cust_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_cust where (name=%s or code=%s) and id!=%s'
        cur.execute(str_sql, args=[name, code, cust_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '名称%s或代号%s重复' % (name, code)
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        e_args = []
        str_tmp = ''
        if code:
            str_tmp = str_tmp + ',code=%s'
            e_args.append(code)
        if name:
            str_tmp = str_tmp + ',name=%s'
            e_args.append(name)
        if status:
            str_tmp = str_tmp + ',status=%s'
            e_args.append(status)
        if bank:
            str_tmp = str_tmp + ',bank=%s'
            e_args.append(bank)
        if account:
            str_tmp = str_tmp + ',account=%s'
            e_args.append(account)
        if credit_code:
            str_tmp = str_tmp + ',credit_code=%s'
            e_args.append(credit_code)
        if address:
            str_tmp = str_tmp + ',address=%s'
            e_args.append(address)
        if contact:
            str_tmp = str_tmp + ',contact=%s'
            e_args.append(contact)
        if phone:
            str_tmp = str_tmp + ',phone=%s'
            e_args.append(phone)
        if email:
            str_tmp = str_tmp + ',email=%s'
            e_args.append(email)
        if status:
            str_tmp = str_tmp + ',status=%s'
            e_args.append(status)
        if remark:
            str_tmp = str_tmp + ',remark=%s'
            e_args.append(remark)
        str_sql = 'update t_cust set ' + str_tmp[1:] + ' where id=%s'
        e_args.append(cust_id)
        cur.execute(str_sql, args=e_args)
        str_msg = '更新客户信息%s' % cust_id
        str_sql = 'insert into t_logs(cust_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 删除
def del_cust(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    cust_id = js['id']
    force = js.get('force', False)
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_cust where id=%s'
        cur.execute(str_sql, args=[cust_id])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s不存在' % cust_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_so where cust_id=%s'
        cur.execute(str_sql, args=[cust_id])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s客户存在销售订单信息，不能删除' % cust_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        if force:
            str_sql = 'delete from t_cust_addr where cust_id=%s'
            cur.execute(str_sql, args=[cust_id])
            str_sql = 'delete from t_cust_contact where cust_id=%s'
            cur.execute(str_sql, args=[cust_id])
            str_sql = 'delete from t_cust_em where cust_id=%s'
            cur.execute(str_sql, args=[cust_id])
        else:
            str_sql = 'update t_cust set status=%s where id=%s'
            cur.execute(str_sql, args=['失效', cust_id])
        str_msg = '删除客户信息%s' % cust_id
        str_sql = 'insert into t_logs(cust_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    js = {'tenant': 'tk_huawei', 'id': 1, 'opt_id': 1}
    print(del_cust(js))


if __name__ == '__main__':
    main()
