# -*- coding: UTF-8 -*-
"""
=================================================
@Project ：tk_smart
@Author ：Ma fei
@Date   ：2022-04-10 06:49
@Desc   ：产品实例管理
==================================================
"""

import datetime
from tk_util import write_log, free_obj, is_none, is_not_none
from db.comm_cnn import CommonCnn


# 查询信息
def get_gd_inst_list(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    name = js.get('name', None)  # 产品名称
    category = js.get('category', None)  # 类别
    code = js.get('code', None)  # 代号
    gb = js.get('gb', None)  # 规格
    alarm = js.get('alarm', None)  # 库存告警
    status = js.get('status', None)  # 产品状态
    u_code = js.get('u_code', None)  # 单位
    page_no = js.get('page_no', 0)
    page_size = js.get('page_size', 0)
    order_field = js.get('order_field', 'id')
    order = js.get('order', 'asc')
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_count = 'select count(a.id) from t_good_inst as a,t_good as b  where a.gd_id=b.id'
        str_sql = 'select a.*,b.name,b.category,b.code,b.gb,b.u_code,b.status from t_good_inst as a,' \
                  't_good as b  where a.gd_id=b.id'
        e_args = []
        if name:
            str_sql = str_sql + ' and b.name=%s'
            str_count = str_count + ' and b.name=%s'
            e_args.append(name)
        if category:
            str_sql = str_sql + ' and b.category=%s'
            str_count = str_count + ' and b.category=%s'
            e_args.append(category)
        if code:
            str_sql = str_sql + ' and b.code=%s'
            str_count = str_count + ' and b.code=%s'
            e_args.append(code)
        if gb:
            str_sql = str_sql + ' and b.gb=%s'
            str_count = str_count + ' and b.gb=%s'
            e_args.append(gb)
        if u_code:
            str_sql = str_sql + ' and b.u_code=%s'
            str_count = str_count + ' and b.u_code=%s'
            e_args.append(u_code)
        if alarm:
            str_sql = str_sql + ' and b.alarm=%s'
            str_count = str_count + ' and b.alarm=%s'
            e_args.append(alarm)
        if status:
            str_sql = str_sql + ' and b.status=%s'
            str_count = str_count + ' and b.status=%s'
            e_args.append(status)
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


# 添加
def add_gd_inst(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    opt_id = js['opt_id']
    gd_id = js.get('gd_id', None)
    if gd_id is None:
        str_msg = '产品ID不能为空，无法创建产品实例信息'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    js_gd_ext = dict()
    for k in js.keys():  # 获取产品扩展属性值
        if k == 'gd_id':
            continue
        js_gd_ext[k] = js[k]
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select name,category,code,gb,u_code from t_good id=%s'
        cur.execute(str_sql, args=[gd_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '产品信息%s不存在，无法创建产品实例信息' % gd_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        name = r[0]
        category = r[1]
        code = [2]
        gb = [3]
        u_code = [4]
        e_args = list()
        s_info = '产品名称%s、类别%s、代号%s、规格%s、单位%s' % (name, category, code, gb, u_code)
        str_sql = 'select count(*) from t_good_inst where gd_id=%s'
        e_args.append(gd_id)
        for k in js_gd_ext.keys():
            str_sql = str_sql + ' and ' + k + '=%s'
            e_args.append(js_gd_ext[k])
        cur.execute(str_sql, args=e_args)
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '该产品实例信息已经存在，无法创建'
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'insert into t_good_inst(gd_id'
        str_end = ') values(%s'
        e_args.clear()  # 清空之前的信息
        e_args.append(gd_id)
        for k in js_gd_ext.keys():
            str_sql = str_sql + ',' + k
            str_end = str_end + ',%s'
            s_info = s_info + ',' + k + '值=' + js_gd_ext[k]
            e_args.append(js_gd_ext[k])
        str_sql = str_sql + str_end
        cur.execute(str_sql, args=e_args)
        str_msg = s_info + ' 添加成功'
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
    stock_id = js.get('stock_id', None)
    wp = js.get('wp', None)
    remark = js.get('remark', None)
    if status:
        if status not in ['有效', '无效']:
            str_msg = '状态必须是\"有效\"或者\"无效\"'
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
    if is_none([name, category, code, gb, u_code, alarm, status, valid_days, stock_id, wp, remark]):
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
        if stock_id:
            str_sql = 'select count(*) from t_stock where id=%s'
            cur.execute(str_sql, args=[stock_id])
            r = cur.fetchone()
            if r[0] == 0:
                str_msg = '无效的仓库信息%s' % stock_id
                js_ret['err_msg'] = str_msg
                write_log(str_msg, tenant=tenant)
                return js_ret
        if wp:
            str_sql = 'select count(*) from t_wp where id=%s'
            cur.execute(str_sql, args=[wp])
            r = cur.fetchone()
            if r[0] == 0:
                str_msg = '无效的工序信息%s' % wp
                js_ret['err_msg'] = str_msg
                write_log(str_msg, tenant=tenant)
                return js_ret
        e_args = []
        str_tmp = ''
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
        if stock_id:
            str_tmp = str_tmp + ',stock_id=%s'
            e_args.append(stock_id)
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
        str_msg = '成功更新物料信息%s' % code
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
        if force:
            str_sql = 'update t_good set status=%s where id=%s'
            cur.execute(str_sql, args=['无效', gd_id])
        else:
            str_sql = 'delete from t_good where id=%s'
            cur.execute(str_sql, args=[gd_id])
        str_sql = 'delete from t_good_inst where gd_id=%s'
        cur.execute(str_sql, args=[gd_id])
        str_sql = 'delete from t_bom where gd_id=%s'
        cur.execute(str_sql, args=[gd_id])
        str_sql = 'delete from t_bom where mate_id=%s'
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
