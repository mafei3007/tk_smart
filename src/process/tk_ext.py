# -*- coding: UTF-8 -*-
"""
=================================================
@Project ：tk_smart
@Author ：Ma fei
@Date   ：2022-04-04 13:12
@Desc   ：扩展属性实例明细管理
首次提交，暂未测试
==================================================
"""

import datetime
from tk_util import write_log, free_obj, is_none, is_not_none
from db.comm_cnn import CommonCnn


# 查询
def get_ext_list(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    ext_type_id = js.get('ext_type_id', None)
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
        str_count = 'select count(a.id) from t_ext as a,t_ext_type as b where a.ext_type_id=b.id'
        str_sql = 'select a.id,a.value,a.remark,b.id as ext_type_id, b.code as ext_code from t_ext as a,' \
                  't_ext_type as b where a.ext_type_id=b.id'
        if ext_type_id:
            str_sql = str_sql + ' and b.id=%s'
            str_count = str_count + ' and b.id=%s'
            qry_args.append(ext_type_id)
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
def add_ext(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    ext_type_id = js.get('ext_type_id', None)
    value = js.get('value', None)
    status = js.get('status', '有效')
    remark = js.get('remark', '')
    if status not in ['有效', '无效']:
        str_msg = '状态必须是\"有效\"或者\"无效\"'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    if is_not_none([ext_type_id, value]):
        str_msg = '元数据、值不能为空.'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select code from t_ext_type where id=%s and status=%s'
        cur.execute(str_sql, args=[ext_type_id, '有效'])
        r = cur.fetchone()
        if r is None:
            str_msg = '不存在有效的扩展类型%s，无法新增扩展属性' % ext_type_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        ext_code = r[0]
        str_sql = 'select count(*) from t_ext where ext_type_id=%s and value=%s'
        cur.execute(str_sql, args=[ext_type_id, value])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '扩展类型%s，值%s的属性实例已经存在，不能重复添加' % (ext_code, value)
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_ext(ext_type_id,value,status,remark) values(%s,%s,%s,%s)'
        cur.execute(str_sql, args=[ext_type_id, value, status, remark])
        str_msg = '创建扩展属性%s，值%s的扩展属性实例信息' % (ext_code, value)
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改
def edit_ext(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    ext_id = js['id']
    ext_type_id = js.get('ext_type_id', None)
    value = js.get('value', None)
    status = js.get('status', None)
    remark = js.get('remark', None)
    if is_none([ext_type_id, value, status, remark]):
        str_msg = '没有需要更新的扩展属性实例信息'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    if status:
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
        str_sql = 'select count(*) from t_ext where id=%s'
        cur.execute(str_sql, args=[ext_id])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '扩展属性实例%s不存在，无法更新' % ext_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        if ext_type_id:
            str_sql = 'select count(*) from t_ext_type where id=%s'
            cur.execute(str_sql, args=[ext_type_id])
            r = cur.fetchone()
            if r[0] > 0:
                str_msg = '扩展类型%s不存在，无法更新' % ext_type_id
                js_ret['err_msg'] = str_msg
                write_log(str_msg, tenant=tenant)
                return js_ret
        str_sql = 'update t_ext set '
        e_args = []
        if ext_type_id:
            str_sql = str_sql + ',ext_type_id=%s'
            e_args.append(ext_type_id)
        if value:
            str_sql = str_sql + ',value=%s'
            e_args.append(value)
        if status:
            str_sql = str_sql + ',status=%s'
            e_args.append(status)
        if remark:
            str_sql = str_sql + ',remark=%s'
            e_args.append(remark)
        str_sql = str_sql + ' where id=%s'
        e_args.append(ext_id)
        cur.execute(str_sql, args=e_args)
        str_msg = '更新扩展属性%s成功' % ext_id
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
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
    opt_id = js['opt_id']
    ext_inst_id = js['id']
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select id from t_ext where id=%s'
        cur.execute(str_sql, args=[ext_inst_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '%s不存在,删除失败' % ext_inst_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_ext where ext_inst_id=%s'
        cur.execute(str_sql, args=[ext_inst_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s被物料引用了，无法删除，自动修改其状态为失效' % ext_inst_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            str_sql = 'update t_ext set status=%s where id=%s'
            cur.execute(str_sql, args=['失效', ext_inst_id])
            return js_ret
        str_sql = 'delete from t_ext where id=%s'
        cur.execute(str_sql, args=[ext_inst_id])
        str_msg = '删除扩展属性信息%s成功' % ext_inst_id
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
    print(del_ext(js))


if __name__ == '__main__':
    main()
