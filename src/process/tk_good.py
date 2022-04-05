# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-30 22:23
@Desc   ：物料管理
==================================================
"""
import datetime
from tk_util import write_log, free_obj, is_none, is_not_none
from db.comm_cnn import CommonCnn


# 查询信息
def get_gd_list(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    name = js.get('name', None)
    category = js.get('category', None)
    code = js.get('code', None)
    gb = js.get('gb', None)
    alarm = js.get('alarm', None)
    status = js.get('status', None)
    u_code = js.get('u_code', None)
    valid_days = js.get('valid_days', None)
    def_stock_id = js.get('def_stock_id', None)
    wp = js.get('wp', None)
    remark = js.get('remark', None)
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
        str_count = 'select count(*) from t_good where 1=1'
        str_sql = 'select * from t_good where 1=1'
        e_args = []
        if name:
            str_sql = str_sql + ' and name=%s'
            str_count = str_count + ' and name=%s'
            e_args.append(name)
        if category:
            str_sql = str_sql + ' and category=%s'
            str_count = str_count + ' and category=%s'
            e_args.append(category)
        if code:
            str_sql = str_sql + ' and code=%s'
            str_count = str_count + ' and code=%s'
            e_args.append(code)
        if gb:
            str_sql = str_sql + ' and gb=%s'
            str_count = str_count + ' and gb=%s'
            e_args.append(gb)
        if u_code:
            str_sql = str_sql + ' and u_code=%s'
            str_count = str_count + ' and u_code=%s'
            e_args.append(u_code)
        if alarm:
            str_sql = str_sql + ' and alarm=%s'
            str_count = str_count + ' and alarm=%s'
            e_args.append(alarm)
        if status:
            str_sql = str_sql + ' and status=%s'
            str_count = str_count + ' and status=%s'
            e_args.append(status)
        if valid_days:
            str_sql = str_sql + ' and valid_days=%s'
            str_count = str_count + ' and valid_days=%s'
            e_args.append(valid_days)
        if def_stock_id:
            str_sql = str_sql + ' and def_stock_id=%s'
            str_count = str_count + ' and def_stock_id=%s'
            e_args.append(def_stock_id)
        if wp:
            str_sql = str_sql + ' and wp=%s'
            str_count = str_count + ' and wp=%s'
            e_args.append(wp)
        if remark:
            str_sql = str_sql + ' and instr(remark,%s)'
            str_count = str_count + ' and instr(remark,%s)'
            e_args.append(remark)
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


# 添加工艺
def add_gd(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    name = js.get('name', None)
    category = js.get('category', None)
    code = js.get('code', None)
    gb = js.get('gb', None)
    u_code = js.get('u_code', None)
    alarm = js.get('alarm', 9999)
    status = js.get('status', '有效')
    valid_days = js.get('valid_days', 3650)
    def_stock_id = js.get('def_stock_id', 0)
    wp = js.get('wp', 0)
    remark = js.get('remark', '')
    if is_not_none([name, category, code, gb, u_code]):
        str_msg = '名称、类别、代号、规格、单位不能为空' % code
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_good where name=%s and category=%s and code=%s and gb=%s and u_code=%s'
        cur.execute(str_sql, args=[name, category, code, gb, u_code])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '物料名称%s、类别%s、代号%s、规格%s、单位%s已经存在，无法新增' % (name, category, code, gb, u_code)
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_unit where u_code=%s'
        cur.execute(str_sql, args=[u_code])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '无效的单位%s,请修改单位信息' % u_code
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_good(name,category,code,gb,u_code,alarm,status,valid_days,def_stock_id,wp,' \
                  'remark) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(str_sql,
                    args=[name, category, code, gb, u_code, alarm, status, valid_days, def_stock_id, wp, remark])
        str_msg = '物料名称%s、类别%s、代号%s、规格%s、单位%s添加成功' % (name, category, code, gb, u_code)
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改
def edit_gd(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    gd_id = js['id']
    name = js.get('name', None)
    category = js.get('category', None)
    code = js.get('code', None)
    gb = js.get('gb', None)
    u_code = js.get('u_code', None)
    alarm = js.get('alarm', None)
    status = js.get('status', None)
    valid_days = js.get('valid_days', None)
    def_stock_id = js.get('def_stock_id', None)
    wp = js.get('wp', None)
    remark = js.get('remark', None)
    # name,category,code,gb,u_code,alarm,status,valid_days,def_stock_id,wp,remark
    if is_none([name, category, code, gb, u_code, alarm, status, valid_days, def_stock_id, wp, remark]):
        str_msg = '没有需要更新的信息'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_good where name=%s and category=%s and code=%s and gb=%s and ' \
                  'u_code=%s and id!=%s'
        cur.execute(str_sql, args=[name, category, code, gb, u_code, gd_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '物料名称%s、类别%s、代号%s、规格%s、单位%s已经存在，无法新增' % (name, category, code, gb, u_code)
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_unit where u_code=%s'
        cur.execute(str_sql, args=[u_code])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '无效的单位%s,请修改物料单位' % u_code
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        e_args = []
        str_tmp = ''
        # name, category, code, gb, u_code, alarm, status, valid_days, def_stock_id, wp, remark
        if name:
            str_tmp = str_tmp + ',name=%s'
            e_args.append(name)
        if category:
            str_tmp = str_tmp + ',category=%s'
            e_args.append(category)
        if code:
            str_tmp = str_tmp + ',code=%s'
            e_args.append(code)
        if gb:
            str_tmp = str_tmp + ',gb=%s'
            e_args.append(gb)
        if u_code:
            str_tmp = str_tmp + ',u_code=%s'
            e_args.append(u_code)
        if alarm:
            str_tmp = str_tmp + ',alarm=%s'
            e_args.append(alarm)
        if status:
            str_tmp = str_tmp + ',status=%s'
            e_args.append(status)
        if valid_days:
            str_tmp = str_tmp + ',valid_days=%s'
            e_args.append(valid_days)
        if def_stock_id:
            str_tmp = str_tmp + ',def_stock_id=%s'
            e_args.append(def_stock_id)
        if wp:
            str_tmp = str_tmp + ',wp=%s'
            e_args.append(wp)
        if remark:
            str_tmp = str_tmp + ',remark=%s'
            e_args.append(remark)
        str_sql = 'update t_good set ' + str_tmp[1:] + ' where id=%s'
        e_args.append(gd_id)
        if len(e_args) > 1:
            cur.execute(str_sql, args=e_args)
        str_msg = '更新物料信息%s' % code
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 删除
def del_gd(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    gd_id = js['id']
    force = js.get('force', False)
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_good where id=%s'
        cur.execute(str_sql, args=[gd_id])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '%s不存在' % gd_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_pc where gd_id=%s'
        cur.execute(str_sql, args=[gd_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s被采购订单引用,无法删除,建议修改状态为失效' % gd_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = True
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_so_detail where gd_id=%s'
        cur.execute(str_sql, args=[gd_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s被销售订单引用,无法删除,建议修改状态为失效' % gd_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_of_detail where gd_id=%s'
        cur.execute(str_sql, args=[gd_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s被询价单引用,无法删除,建议修改状态为失效' % gd_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_checkin where gd_id=%s'
        cur.execute(str_sql, args=[gd_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s存在入库记录,无法删除,建议修改状态为失效' % gd_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_checkout where gd_id=%s'
        cur.execute(str_sql, args=[gd_id])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '%s存在出库记录,无法删除,建议修改状态为失效' % gd_id
            js_ret['err_msg'] = str_msg
            js_ret['result'] = False
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'delete from t_good where id=%s'
        cur.execute(str_sql, args=[gd_id])
        str_msg = '删除物料%s' % gd_id
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    js = {'tenant': 'tk_huawei', 'id': 123, 'opt_id': 1}
    print(del_gd(js))


if __name__ == '__main__':
    main()
