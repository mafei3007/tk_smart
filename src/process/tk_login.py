# -*- coding: UTF-8 -*-
"""
=================================================
@Project ：tk_smart
@Author ：Ma fei
@Date   ：2022-04-03 13:46
@Desc   ：
==================================================
"""

from tk_util import write_log, free_obj, des_encrypt, check_pwd
from db.comm_cnn import CommonCnn
from constant import default_pwd


# 用户登录
def login(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    code = js['code']
    password = js['password']
    encrypt_pwd = des_encrypt(code + password)
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select password from t_em where code=%s'
        cur.execute(str_sql, args=[code])
        r = cur.fetchone()
        if r is None:
            str_msg = '错误的用户名或密码'
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        db_encrypt_pwd = r[0]  # 11a4627cd0dc9d2d
        print(encrypt_pwd, db_encrypt_pwd)
        if db_encrypt_pwd != encrypt_pwd:
            str_msg = '用户%s登录鉴权失败' % code
            str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
            cur.execute(str_sql, args=[opt_id, str_msg])
            write_log(str_msg, tenant=tenant)
            str_msg = '错误的用户名或密码'
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_msg = '%s登录系统' % code
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改密码
def change_pwd(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    code = js['code']
    password = js['password']
    new_password = js['new_password']
    str_msg = check_pwd(new_password)
    if str_msg:
        js_ret['err_msg'] = str_msg
        js_ret['result'] = False
        write_log(str_msg, tenant=tenant)
        return js_ret
    encrypt_pwd = des_encrypt(code + password)
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select password from t_em where code=%s'
        cur.execute(str_sql, args=[code])
        r = cur.fetchone()
        if r is None:
            str_msg = '用户%s不存在，无法修改密码' % code
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        db_encrypt_pwd = r[0]  # 11a4627cd0dc9d2d
        if db_encrypt_pwd != encrypt_pwd:
            str_msg = '用户%s原密码鉴权失败，无法修改密码' % code
            str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
            cur.execute(str_sql, args=[opt_id, str_msg])
            write_log(str_msg, tenant=tenant)
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            return js_ret
        encrypt_pwd = des_encrypt(code + new_password)
        str_sql = 'update t_em set password=%s where code=%s'
        cur.execute(str_sql, args=[encrypt_pwd, code])
        str_msg = '%s的密码修改成功' % code
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['err_msg'] = str_msg
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 重置密码
def reset_pwd(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    code = js['code']
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select password from t_em where id=%s'
        cur.execute(str_sql, args=[opt_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '用户%s不存在，无法重置密码' % code
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select password from t_em where code=%s'
        cur.execute(str_sql, args=[code])
        r = cur.fetchone()
        if r is None:
            str_msg = '用户%s不存在，无法修改密码' % code
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        encrypt_pwd = des_encrypt(code + default_pwd)
        str_sql = 'update t_em set password=%s where code=%s'
        cur.execute(str_sql, args=[encrypt_pwd, code])
        str_msg = '%s的密码重置成功' % code
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['err_msg'] = str_msg
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    js = {'tenant': 'tk_huawei', 'code': 'gj', 'password': '123', 'opt_id': 1}
    print(login(js))


if __name__ == '__main__':
    main()
