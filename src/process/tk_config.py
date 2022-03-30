# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-28 08:36
@Desc   ：单位管理
==================================================
"""
import datetime
from src.tk_util import write_log
from process.srv_util import get_tenant_cnn, free_obj
from src.constant import company_name, company_bank, company_account, company_credit_code, company_address


# 获取序号
def get_idx(tenant, code):
    ret_idx = 1000
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select idx from t_sys where code=%s'
        cur.execute(str_sql, args=[code])
        r = cur.fetchone()
        if r is None:
            str_sql = 'insert into t_sys(code,idx) values(%s,%s)'
            cur.execute(str_sql, args=[code, ret_idx])
            return ret_idx
        ret_idx += 1
        str_sql = 'update t_sys set idx=idx+1 where code=%s'
        cur.execute(str_sql, args=[code])
        return ret_idx
    finally:
        free_obj(cur)
        cnn.close()


def get_config(tenant, k, def_v):
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select v from t_config where k=%s'
        str_msg = 'SQL:%s,参数:%s' % (str_sql, k)
        write_log(str_msg, tenant=tenant)
        cur.execute(str_sql, args=[k])
        r = cur.fetchone()
        if r is None:
            str_sql = 'insert into t_config(k,v) values(%s,%s)'
            cur.execute(str_sql, args=[k, def_v])
            return def_v
        return r[0]
    finally:
        free_obj(cur)
        cnn.close()


def set_config(tenant, k, v):
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'delete from t_config where k=%s'
        cur.execute(str_sql, args=[k])
        str_sql = 'insert into t_config(k,v) values(%s,%s)'
        cur.execute(str_sql, args=[k, v])
    finally:
        free_obj(cur)
        cnn.close()


# 查询公司信息
def get_company(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = dict()
    tenant = js['tenant']
    js_ret['data']['company_name'] = get_config(tenant, company_name, '公司名称')
    js_ret['data']['company_bank'] = get_config(tenant, company_bank, '开户行')
    js_ret['data']['company_account'] = get_config(tenant, company_account, '银行账户')
    js_ret['data']['company_credit_code'] = get_config(tenant, company_credit_code, '统一信用代码')
    js_ret['data']['company_address'] = get_config(tenant, company_address, '注册地址')
    return js_ret


# 获取公司联系人信息
def get_company_ext(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select * from t_company'
        str_msg = '查询SQL:%s,参数:空' % str_sql
        write_log(str_msg, tenant=tenant)
        cur.execute(str_sql)
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


# 添加信息
def add_ext(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    name = js['name']
    address = js['address']
    contact = js['contact']
    phone = js['phone']
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_company where name=%s'
        cur.execute(str_sql, args=[name])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s已经存在，无法添加' % name
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_company(name,address,contact,phone) values(%s,%s,%s,%s)'
        cur.execute(str_sql, args=[name, address, contact, phone])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改扩展信息
def edit_ext(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    ext_id = js['id']
    name = js.get('name', None)
    address = js.get('address', None)
    contact = js.get('contact', None)
    phone = js.get('phone', None)
    if name is None:
        str_msg = '名称不能为空，无法编辑'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_company where name=%s and id=%s'
        cur.execute(str_sql, args=[name, ext_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s已经存在，无法添加' % name
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'update t_company set name=%s'
        e_args = [name]
        if address:
            str_sql = str_sql + ',address=%s'
            e_args.append(address)
        if contact:
            str_sql = str_sql + ',contact=%s'
            e_args.append(contact)
        if phone:
            str_sql = str_sql + ',phone=%s'
            e_args.append(phone)
        str_sql = str_sql + ' where id=%s'
        e_args.append(ext_id)
        cur.execute(str_sql, args=e_args)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 删除
def del_ext(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    ext_id = js['id']
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'delete from t_company where id=%s'
        cur.execute(str_sql, args=[ext_id])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    js = {'tenant': 'tk_huawei'}
    print(get_company(js))
    # js = {'tenant': 'tk_huawei', 'name': '怡红院', 'address': '陕西平川', 'contact': '习近平', 'phone': '13388889999'}
    # print(add_ext(js))
    # js = {'tenant': 'tk_huawei', 'name': '总部', 'address': '北京东路1号', 'contact': '马飞', 'phone': '12999998888'}
    # print(add_ext(js))
    # js = {'tenant': 'tk_huawei', 'id': 99}
    # print(del_ext(js))


if __name__ == '__main__':
    main()
