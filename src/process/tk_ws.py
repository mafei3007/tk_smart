# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-04-01 20:10
@Desc   ：工艺管理 具体的加工方法，如切割 成型 包塑 等
==================================================
"""
import datetime
from tk_util import write_log, free_obj, is_none
from db.comm_cnn import CommonCnn


# 查询信息
def get_ws(js):
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
        e_args = []
        str_sql = 'select id,code,status,remark from t_ws order by code asc'
        cur.execute(str_sql, args=e_args)
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
def add_ws(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    code = js['code']
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
        str_sql = 'select count(*) from t_ws where code=%s'
        cur.execute(str_sql, args=[code])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '工艺%s已经存在，不能重复添加' % code
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_ws(code,status,remark) values(%s,%s,%s)'
        cur.execute(str_sql, args=[code, status, remark])
        str_msg = '添加工艺,代号%s' % code
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改
def edit_ws(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    ws_id = js['id']
    code = js.get('code', None)
    status = js.get('status', None)
    remark = js.get('remark', None)
    if is_none([code, status, remark]):
        str_msg = '没有需要更新的信息'
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
        str_sql = 'select count(*) from t_ws where id=%s'
        cur.execute(str_sql, args=[ws_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '工艺%s不存在，无法更新' % code
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        if code:
            str_sql = 'select count(*) from t_ws where id！=%s and code=%s'
            cur.execute(str_sql, args=[ws_id, code])
            r = cur.fetchone()
            if r[0] > 0:
                str_msg = '工艺%s重复，无法更新' % code
                js_ret['err_msg'] = str_msg
                write_log(str_msg, tenant=tenant)
                return js_ret
        e_args = []
        str_tmp = ''
        if code:
            str_tmp = str_tmp + ',code=%s'
            e_args.append(code)
        if status:
            str_tmp = str_tmp + ',status=%s'
            e_args.append(status)
        if remark:
            str_tmp = str_tmp + ',remark=%s'
            e_args.append(remark)
        str_sql = 'update t_ws set ' + str_tmp[1:] + ' where id=%s'
        e_args.append(ws_id)
        if len(e_args) > 1:
            cur.execute(str_sql, args=e_args)
        str_msg = '更新工艺信息%s' % code
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 删除
def del_ws(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    ws_id = js['id']
    force = js.get('force', False)
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_ws where id=%s'
        cur.execute(str_sql, args=[ws_id])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s不存在' % ws_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        if force:
            str_sql = 'delete from t_ws where id=%s'
            cur.execute(str_sql, args=[ws_id])
        else:
            str_sql = 'update t_ws set status=%s where id=%s'
            cur.execute(str_sql, args=['失效', ws_id])
        str_msg = '删除工艺信息%s' % ws_id
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
    print(del_ws(js))


if __name__ == '__main__':
    main()
