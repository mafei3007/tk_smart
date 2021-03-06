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
from tk_util import write_log, free_obj, is_none, is_not_none
from db.comm_cnn import CommonCnn
from constant import comm_unit_type


# 查询信息
def get_unit(js):
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
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        qry_args = []
        str_sql = 'select u_code,u_type,basic_unit,conversion_rate,dt,remark from t_unit'
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


# 添加
def add_unit(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    u_code = js.get('u_code', None)
    u_type = js.get('u_type', None)
    basic_unit = js.get('basic_unit', None)
    conversion_rate = js.get('remark', 1)
    remark = js.get('remark', '')
    if is_not_none([u_code, u_type, basic_unit]):
        str_msg = '单位代号/类型/基础单位不能为空' % u_code
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    if u_type not in comm_unit_type:  # 单位类型必须合法
        str_msg = '%s类型不正确，只能是%s，无法添加' % (u_code, str(comm_unit_type))
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    if basic_unit == u_code and conversion_rate != 1:
        str_msg = '%s为基础单位，换算率必须要为1，否则无法添加' % u_code
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        if basic_unit != u_code:  # 不是基础单位，那就需要判断该单位的基础单位是否存在
            str_sql = 'select count(*) from t_unit where u_code=%s'
            cur.execute(str_sql, args=[basic_unit])
            r = cur.fetchone()
            if r[0] == 0:  # 该单位的基础单位不存在，报错
                str_msg = '%s的基础单位%s不存在，无法添加' % (u_code, basic_unit)
                write_log(str_msg, tenant=tenant)
                return js_ret
        str_sql = 'select count(*) from t_unit where u_code=%s'
        cur.execute(str_sql, args=[u_code])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s已经存在，不能重复添加' % u_code
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_unit(u_code,u_type,basic_unit,conversion_rate,remark) values(%s,%s,%s,%s,%s)'
        cur.execute(str_sql, args=[u_code, u_type, basic_unit, conversion_rate, remark])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改，code 不能修改
def edit_unit(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    u_code = js['u_code']
    u_type = js.get('u_type', None)
    conversion_rate = js.get('conversion_rate', None)
    basic_unit = js.get('basic_unit', None)
    remark = js.get('remark', None)
    if is_none([u_type, conversion_rate, basic_unit, remark]):
        str_msg = '没有需要更新的信息'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    if basic_unit == u_code and (conversion_rate and conversion_rate != 1):
        str_msg = '%s为基础单位，换算率必须要为1，否则无法编辑' % u_code
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    if u_type != '' and u_type not in comm_unit_type:
        str_msg = '%s类型不正确，只能是%s，无法编辑' % (u_code, str(comm_unit_type))
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_unit where u_code=%s'
        cur.execute(str_sql, args=[u_code])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s不存在，无法编辑' % u_code
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        if basic_unit != '' and basic_unit != u_code:  # 不是基础单位，那就需要判断该单位的基础单位是否存在
            str_sql = 'select count(*) from t_unit where u_code=%s'
            cur.execute(str_sql, args=[basic_unit])
            r = cur.fetchone()
            if r[0] == 0:  # 该单位的基础单位不存在，报错
                str_msg = '%s的基础单位%s不存在，无法编辑' % (u_code, basic_unit)
                js_ret['err_msg'] = str_msg
                write_log(str_msg, tenant=tenant)
                return js_ret
        e_args = []
        str_tmp = ''
        if u_type:
            str_tmp = str_tmp + ',u_type=%s'
            e_args.append(u_type)
        if basic_unit:
            str_tmp = str_tmp + ',basic_unit=%s'
            e_args.append(basic_unit)
        if conversion_rate:
            str_tmp = str_tmp + ',conversion_rate=%s'
            e_args.append(conversion_rate)
        if remark:
            str_tmp = str_tmp + ',remark=%s'
            e_args.append(remark)
        str_sql = 'update t_unit set' + str_tmp[1:] + ' where u_code=%s'
        e_args.append(u_code)
        if len(e_args) > 1:
            cur.execute(str_sql, args=e_args)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 删除
def del_unit(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    u_code = js['u_code']
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_unit where u_code=%s'
        cur.execute(str_sql, args=[u_code])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s不存在' % u_code
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_good where u_code=%s'
        cur.execute(str_sql, args=[u_code])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s已经被产品引用，无法删除' % u_code
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'delete from t_unit where u_code=%s'
        cur.execute(str_sql, args=[u_code])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    js = {'tenant': 'tk_huawei', 'opt_id': 1}
    print(del_unit(js))


if __name__ == '__main__':
    main()
