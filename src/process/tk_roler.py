# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-28 08:36
@Desc   ：角色管理
==================================================
"""
import datetime
from tk_util import write_log
from process.srv_util import get_tenant_cnn, free_obj
from constant import comm_role


# 查询角色信息
def get_role(js):
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
        str_sql = 'select * from t_role'
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


# 添加角色
def add_role(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    name = js['name']
    remark = js.get('remark', '')
    if name in comm_role:
        str_msg = '%s为系统默认角色，无法重复添加' % name
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_role where name=%s'
        cur.execute(str_sql, args=[name])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s已经存在，不能重复添加' % name
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_role(name,rights,remark) values(%s,%s,%s)'
        cur.execute(str_sql, args=[name, '0', remark])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改角色
def edit_role(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    rl_id = js['id']
    name = js['name']
    rights = js.get('rights', '')
    remark = js.get('remark', '')
    cnn = None
    cur = None
    if name in comm_role:
        str_msg = '%s为系统默认角色，无法修改信息' % name
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_role where id=%s and default=%s'
        cur.execute(str_sql, args=[rl_id, '系统'])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s为系统默认角色，无法修改信息' % rl_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_role where id=%s'
        cur.execute(str_sql, args=[rl_id, '系统'])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s角色不存在，无法修改信息' % rl_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'update t_role set name=%s'
        e_args = [name]
        if rights != '':
            str_sql = str_sql + ',rights=%s'
            e_args.append(rights)
        if remark != '':
            str_sql = str_sql + ',remark=%s'
            e_args.append(remark)
        str_sql = str_sql + ' where id=%s'
        e_args.append(rl_id)
        cur.execute(str_sql, args=e_args)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 删除角色
def del_role(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    rl_id = js['id']
    force = js.get('force', False)
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_role where id=%s and default=%s'
        cur.execute(str_sql, args=[rl_id, '系统'])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s为系统默认角色，无法删除' % rl_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_role where id=%s'
        cur.execute(str_sql, args=[rl_id, '系统'])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s角色不存在，无法删除信息' % rl_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        if not force:  # 如果不支持级联删除
            str_sql = 'select count(*) from t_em_role where rl_id=%s'
            cur.execute(str_sql, args=[rl_id])
            r = cur.fetchone()
            if r[0] > 0:
                str_msg = '%s角色已经被用户引用，无法删除信息' % rl_id
                js_ret['err_msg'] = str_msg
                js_ret['result'] = False
                write_log(str_msg, tenant=tenant)
                return js_ret
        str_sql = 'delete from t_role where id=%s'
        cur.execute(str_sql, args=[rl_id])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    js = {'tenant': 'tk_huawei'}
    print(get_role(js))


if __name__ == '__main__':
    main()
