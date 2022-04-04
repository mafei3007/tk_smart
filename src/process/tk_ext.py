# -*- coding: UTF-8 -*-
"""
=================================================
@Project ：tk_smart
@Author ：Ma fei
@Date   ：2022-04-04 12:54
@Desc   ：物料扩展属性管理
==================================================
"""

import datetime
from tk_util import write_log, free_obj
from db.comm_cnn import CommonCnn


# 查询
def get_ext_list(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        qry_args = []
        str_sql = 'select * from t_ext order by code asc'
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


# 添加
def add_ext(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    code = js['code']
    elastic = js.get('elastic', '否')
    basic_unit = js.get('basic_unit', None)
    remark = js.get('remark', '')
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_ext where code=%s'
        cur.execute(str_sql, args=[code])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s已经存在，不能重复添加' % code
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_ext(code,elastic,basic_unit,remark) values(%s,%s,%s,%s)'
        cur.execute(str_sql, args=[code, elastic, basic_unit, remark])
        str_msg = '添加扩展属性%s' % code
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
    code = js.get('code', None)
    elastic = js.get('elastic', None)
    basic_unit = js.get('basic_unit', None)
    remark = js.get('remark', '')
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_ext where id=%s'
        cur.execute(str_sql, args=[ext_id])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '扩展属性%s不存在，无法更新' % ext_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        if code:
            str_sql = 'select count(*) from t_ext where id!=%s and code=%s'
            cur.execute(str_sql, args=[ext_id, code])
            r = cur.fetchone()
            if r[0] > 0:
                str_msg = '扩展属性代号%s不能重复，无法更新' % code
                js_ret['err_msg'] = str_msg
                write_log(str_msg, tenant=tenant)
                return js_ret
        str_sql = 'update t_ext set remark=%s'
        e_args = [remark]
        if code:
            str_sql = str_sql + ',code=%s'
            e_args.append(code)
        if elastic:
            str_sql = str_sql + ',elastic=%s'
            e_args.append(elastic)
        if basic_unit:
            str_sql = str_sql + ',basic_unit=%s'
            e_args.append(basic_unit)
        str_sql = str_sql + ' where id=%s'
        e_args.append(ext_id)
        cur.execute(str_sql, args=e_args)
        str_msg = '更新扩展属性信息%s' % code
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
    ext_id = js['id']
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select id from t_ext where id=%s'
        cur.execute(str_sql, args=[ext_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '%s不存在,删除失败' % ext_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_ext_detail where ext_id=%s'
        cur.execute(str_sql, args=[ext_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s被工序引用了，无法删除' % ext_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'delete from t_ext where id=%s'
        cur.execute(str_sql, args=[ext_id])
        str_msg = '删除工艺信息%s' % ext_id
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
