# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-04-01 19:23
@Desc   ：供货商管理
==================================================
"""
import datetime
from tk_util import write_log, free_obj, is_none
from db.comm_cnn import CommonCnn


# 查询人员列表信息
def get_sp_list(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    name = js.get('name', None)
    code = js.get('code', None)
    status = js.get('status', '有效')
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
        str_count = 'select count(*) from t_supp where status=%s'
        str_sql = 'select * from t_supp where status=%s'
        qry_args.append(status)
        if name:
            str_sql = str_sql + ' and name=%s'
            str_count = str_count + ' and name=%s'
            qry_args.append(name)
        if code:
            str_sql = str_sql + ' and code=%s'
            str_count = str_count + ' and code=%s'
            qry_args.append(code)
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


# 添加人员
def add_sp(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    name = js['name']
    code = js['code']
    contact = js.get('contact', '')
    contact_phone = js.get('contact_phone', '')
    em_id = js.get('em_id', 0)
    status = js.get('status', '有效')
    bank = js.get('bank', '')
    account = js.get('account', '')
    credit_code = js.get('credit_code', '')
    phone = js.get('phone', '')
    address = js.get('address', '')
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
        str_sql = 'select count(*) from t_sp where name=%s or code=%s'
        cur.execute(str_sql, args=[name, code])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '姓名%s或代号%s已经存在，不能重复添加' % (name, code)
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_supp(name,code,contact,contact_phone,em_id,status,bank,account,credit_code,' \
                  'phone,address,remark) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(str_sql,
                    args=[name, code, contact, contact_phone, em_id, status, bank, account, credit_code, phone, address,
                          remark])
        str_msg = '添加供货商：名称%s,代号%s' % (name, code)
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改人员
def edit_sp(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    sp_id = js['id']
    name = js.get('name', None)
    code = js.get('code', None)
    contact = js.get('contact', None)
    contact_phone = js.get('contact_phone', None)
    em_id = js.get('em_id', None)
    status = js.get('status', None)
    bank = js.get('bank', None)
    account = js.get('account', None)
    credit_code = js.get('credit_code', None)
    phone = js.get('phone', None)
    address = js.get('address', None)
    remark = js.get('remark', None)
    if status:
        if status not in ['有效', '无效']:
            str_msg = '状态必须是\"有效\"或者\"无效\"'
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
    if is_none([name, code, contact, contact_phone, em_id, status, bank, account, credit_code, phone, address, remark]):
        str_msg = '没有需要更新的信息'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_supp where id=%s'
        cur.execute(str_sql, args=[em_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '供货商信息%s不存在，无法删除' % em_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_supp where (name=%s or code=%s) and id!=%s'
        cur.execute(str_sql, args=[name, code, sp_id])
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
        if contact:
            str_tmp = str_tmp + ',contact=%s'
            e_args.append(contact)
        if contact_phone:
            str_tmp = str_tmp + ',contact_phone=%s'
            e_args.append(phone)
        if em_id:
            str_tmp = str_tmp + ',em_id=%s'
            e_args.append(em_id)
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
        if phone:
            str_tmp = str_tmp + ',phone=%s'
            e_args.append(phone)
        if address:
            str_tmp = str_tmp + ',account=%s'
            e_args.append(address)
        if remark:
            str_tmp = str_tmp + ',remark=%s'
            e_args.append(remark)
        str_sql = 'update t_supp set ' + str_tmp[1:] + ' where id=%s'
        e_args.append(em_id)
        cur.execute(str_sql, args=e_args)
        str_msg = '更新供货商信息%s' % em_id
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 删除人员
def del_sp(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    sp_id = js['id']
    force = js.get('force', False)
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_supp where id=%s'
        cur.execute(str_sql, args=[sp_id])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s不存在' % sp_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_pc where sp_id=%s'
        cur.execute(str_sql, args=[sp_id])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s存在采购信息，不能删除' % sp_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        if force:
            str_sql = 'delete from t_supp where id=%s'
            cur.execute(str_sql, args=[sp_id])
        else:
            str_sql = 'update t_supp set status=%s where id=%s'
            cur.execute(str_sql, args=['失效', sp_id])
        str_msg = '删除供货商信息%s' % sp_id
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    js = {'tenant': 'tk_huawei', 'id': 567, 'opt_id': 1}
    print(del_sp(js))


if __name__ == '__main__':
    main()
