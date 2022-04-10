# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-30 22:23
@Desc   ：产品管理
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
    name = js.get('name', None)  # 产品名称
    category = js.get('category', None)  # 类别
    code = js.get('code', None)  # 代号
    gb = js.get('gb', None)  # 规格
    alarm = js.get('alarm', None)  # 库存告警
    status = js.get('status', None)  # 产品状态
    u_code = js.get('u_code', None)  # 单位
    valid_days = js.get('valid_days', None)  # 有效期
    stock_id = js.get('stock_id', None)  # 默认仓库
    stock_name = js.get('stock_name', None)  # 默认仓库
    wp = js.get('wp', None)  # 产品工序
    remark = js.get('remark', None)
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
        str_sql = 'select a.id,a.name,a.category,a.code,a.gb,a.u_code,a.alarm,a.status,a.valid_days,' \
                  'a.stock_id,a.wp,a.remark,a.dt,b.name as stock_name from t_good as a,t_stock as b where ' \
                  'a.stock_id=b.id'
        str_count = 'select count(a.id) from t_good as a,t_stock as b where a.stock_id=b.id'
        e_args = []
        if name:
            str_sql = str_sql + ' and a.name=%s'
            str_count = str_count + ' and a.name=%s'
            e_args.append(name)
        if category:
            str_sql = str_sql + ' and a.category=%s'
            str_count = str_count + ' and a.category=%s'
            e_args.append(category)
        if code:
            str_sql = str_sql + ' and a.code=%s'
            str_count = str_count + ' and a.code=%s'
            e_args.append(code)
        if gb:
            str_sql = str_sql + ' and a.gb=%s'
            str_count = str_count + ' and a.gb=%s'
            e_args.append(gb)
        if u_code:
            str_sql = str_sql + ' and a.u_code=%s'
            str_count = str_count + ' and a.u_code=%s'
            e_args.append(u_code)
        if alarm:
            str_sql = str_sql + ' and a.alarm=%s'
            str_count = str_count + ' and a.alarm=%s'
            e_args.append(alarm)
        if status:
            str_sql = str_sql + ' and a.status=%s'
            str_count = str_count + ' and a.status=%s'
            e_args.append(status)
        if valid_days:
            str_sql = str_sql + ' and a.valid_days=%s'
            str_count = str_count + ' and a.valid_days=%s'
            e_args.append(valid_days)
        if stock_id:
            str_sql = str_sql + ' and a.stock_id=%s'
            str_count = str_count + ' and a.stock_id=%s'
            e_args.append(stock_id)
        if stock_name:
            str_sql = str_sql + ' and b.name=%s'
            str_count = str_count + ' and b.name=%s'
            e_args.append(stock_name)
        if wp:
            str_sql = str_sql + ' and a.wp=%s'
            str_count = str_count + ' and a.wp=%s'
            e_args.append(wp)
        if remark:
            str_sql = str_sql + ' and instr(a.remark,%s)'
            str_count = str_count + ' and instr(a.remark,%s)'
            e_args.append(remark)
        if start_dt:
            str_sql = str_sql + ' and a.dt>=%s'
            str_count = str_count + ' and a.dt>=%s'
            e_args.append(start_dt)
        if end_dt:
            str_sql = str_sql + ' and a.dt<=%s'
            str_count = str_count + ' and a.dt<=%s'
            e_args.append(end_dt)
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
    stock_id = js.get('stock_id', None)
    wp = js.get('wp', None)
    remark = js.get('remark', '')
    if status not in ['有效', '无效']:
        str_msg = '状态必须是\"有效\"或者\"无效\"'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    if is_not_none([name, category, code, gb, u_code]):
        str_msg = '名称、类别、代号、规格、单位不能为空'
        js_ret['err_msg'] = str_msg
        write_log(str_msg, tenant=tenant)
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select count(*) from t_stock where status=%s'
        cur.execute(str_sql, args=['有效'])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '当前系统中没有可用的仓库信息，请先配置仓库信息'
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_wp where status=%s'
        cur.execute(str_sql, args=['有效'])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '当前系统中没有可用的工序信息，请先配置工序信息'
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_good where name=%s and category=%s and code=%s and gb=%s and u_code=%s'
        cur.execute(str_sql, args=[name, category, code, gb, u_code])
        r = cur.fetchone()
        if r[0] > 0:
            str_msg = '产品名称%s、类别%s、代号%s、规格%s、单位%s已经存在，无法新增' % (name, category, code, gb, u_code)
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
        if stock_id:
            str_sql = 'select count(*) from t_stock where id=%s'
            cur.execute(str_sql, args=[stock_id])
            r = cur.fetchone()
            if r[0] == 0:
                str_msg = '无效的仓库信息%s' % stock_id
                js_ret['err_msg'] = str_msg
                write_log(str_msg, tenant=tenant)
                return js_ret
        else:
            str_sql = 'select id from t_stock order by id asc limit 1'
            cur.execute(str_sql, args=[stock_id])
            r = cur.fetchone()
            stock_id = r[0]
        if wp:
            str_sql = 'select count(*) from t_wp where id=%s'
            cur.execute(str_sql, args=[wp])
            r = cur.fetchone()
            if r[0] == 0:
                str_msg = '无效的工序信息%s' % wp
                js_ret['err_msg'] = str_msg
                write_log(str_msg, tenant=tenant)
                return js_ret
        else:
            str_sql = 'select id from t_wp order by id asc limit 1'
            cur.execute(str_sql, args=[wp])
            r = cur.fetchone()
            wp = r[0]
        str_sql = 'insert into t_good(name,category,code,gb,u_code,alarm,status,valid_days,stock_id,wp,' \
                  'remark) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(str_sql,
                    args=[name, category, code, gb, u_code, alarm, status, valid_days, stock_id, wp, remark])
        str_sql = 'select count(*) from t_good where name=%s and category=%s and code=%s and gb=%s and u_code=%s'
        cur.execute(str_sql, args=[name, category, code, gb, u_code])
        r = cur.fetchone()
        gd_id = r[0]  # 刚新增的产品ID
        str_sql = 'insert into t_good_inst(gd_id) values(%s)'
        cur.execute(str_sql, args=[gd_id])
        str_sql = 'select id from t_good_inst where gd_id=%s'
        cur.execute(str_sql, args=[gd_id])
        r = cur.fetchone()
        gd_inst_id = r[0]
        str_msg = '产品名称:%s、类别:%s、代号:%s、规格:%s、单位:%s添加成功，产品ID:%s，产品实例ID:' \
                  '%s' % (name, category, code, gb, u_code, gd_id, gd_inst_id)
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
            str_msg = '产品名称:%s、类别:%s、代号:%s、规格:%s、单:位%s已经存在，无法新增' % (name, category, code, gb, u_code)
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        str_sql = 'select count(*) from t_unit where u_code=%s'
        cur.execute(str_sql, args=[u_code])
        r = cur.fetchone()
        if r[0] == 0:
            str_msg = '无效的单位%s,请修改产品单位' % u_code
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
        str_msg = '成功更新产品信息%s' % code
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
        str_msg = '删除产品%s' % gd_id
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
