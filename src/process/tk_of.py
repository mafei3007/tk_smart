# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-28 08:36
@Desc   ：询价单管理
==================================================
"""
import datetime
import threading
import time

from tk_util import write_log
from process.srv_util import get_tenant_cnn, free_obj
from src.process.tk_config import get_idx

lock = threading.Lock()


def get_pc_name(tenant):
    code = 'PC'
    lock.acquire()
    try:
        pc_name = code + '_' + time.strftime('%Y%m%d', time.localtime(time.time())) + '_%d' % get_idx(tenant, code)
        str_msg = '获取订单名称%s' % pc_name
        write_log(str_msg, tenant=tenant)
        return pc_name
    finally:
        lock.release()


# 查询支付记录
def get_pc_paid_info(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    pc_id = js.get('pc_id', 0)
    sp_id = js.get('sp_id', 0)
    em_id = js.get('em_id', 0)
    start_dt = js.get('start_dt', None)
    end_dt = js.get('end_dt', None)
    page_no = js.get('page_no', 0)
    page_size = js.get('page_size', 0)
    order_field = js.get('order_field', 'id')
    order = js.get('order', 'asc')
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        qry_args = []
        str_count = 'select count(b.id) from t_pc as a,t_pc_pay as b,t_em as c, t_supp as d,t_good as e ' \
                    'where a.id=b.pc_id and a.sp_id=d.id and b.em_id=c.id and a.gd_id=e.id '
        str_sql = 'select b.id,a.gd_id,a.dt as pc_dt, a.count as pc_count,a.sp_id,a.to_pay_amount,a.paid_amount,' \
                  'b.amount,b.dt as pay_dt,c.name as em_name,d.name as sp_name,e.name as gd_name,e.code ' \
                  'as gb_code,e.gb from t_pc as a,t_pc_pay as b,t_em as c, t_supp as d,t_good as e where ' \
                  'a.id=b.pc_id and a.sp_id=d.id and b.em_id=c.id and a.gd_id=e.id '
        if pc_id > 0:
            str_sql = str_sql + ' and a.id=%s'
            str_count = str_count + ' and a.id=%s'
            qry_args.append(pc_id)
        if sp_id > 0:
            str_sql = str_sql + ' and a.sp_id=%s'
            str_count = str_count + ' and a.id=%s'
            qry_args.append(sp_id)
        if em_id > 0:
            str_sql = str_sql + ' and b.em_id=%s'
            str_count = str_count + ' and b.em_id=%s'
            qry_args.append(em_id)
        if start_dt:
            str_sql = str_sql + ' and b.dt>=%s'
            str_count = str_count + ' and b.dt>=%s'
            qry_args.append(start_dt)
        if end_dt:
            str_sql = str_sql + ' and b.dt<=%s'
            str_count = str_count + ' and b.dt<=%s'
            qry_args.append(end_dt)
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


# 查询进货记录
def get_pc_checkin(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    pc_id = js.get('pc_id', 0)
    sp_id = js.get('sp_id', 0)
    em_id = js.get('em_id', 0)
    start_dt = js.get('start_dt', None)
    end_dt = js.get('end_dt', None)
    page_no = js.get('page_no', 0)
    page_size = js.get('page_size', 0)
    order_field = js.get('order_field', 'id')
    order = js.get('order', 'asc')
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        qry_args = []
        str_count = 'select count(a.gd_id) from t_checkin as a,t_pc as b,t_em as c, t_stock as d, t_supp as e,' \
                    't_good as f where a.pc_id=b.id and a.em_id=c.id and a.stock_id=d.id and b.sp_id=e.id ' \
                    'and b.gd_id=f.id '
        str_sql = 'select a.gd_id,a.dt as checkin_dt, a.count as checkin_count,a.barcode,b.name as pc_name,' \
                  'b.count as pc_count,b.rec_count,b.dt as pc_dt, c.name as em_name, d.name as stock_name,' \
                  'e.name as sp_name,f.name as gd_name,f.code as gd_code,f.gb as gd_gb from t_checkin as a,' \
                  't_pc as b,t_em as c, t_stock as d, t_supp as e,t_good as f where a.pc_id=b.id and ' \
                  'a.em_id=c.id and a.stock_id=d.id and b.sp_id=e.id and b.gd_id=f.id '
        if pc_id > 0:
            str_sql = str_sql + ' and b.id=%s'
            str_count = str_count + ' and b.id=%s'
            qry_args.append(pc_id)
        if sp_id > 0:
            str_sql = str_sql + ' and b.sp_id=%s'
            str_count = str_count + ' and b.id=%s'
            qry_args.append(sp_id)
        if em_id > 0:
            str_sql = str_sql + ' and b.em_id=%s'
            str_count = str_count + ' and b.em_id=%s'
            qry_args.append(em_id)
        if start_dt:
            str_sql = str_sql + ' and a.dt>=%s'
            str_count = str_count + ' and a.dt>=%s'
            qry_args.append(start_dt)
        if end_dt:
            str_sql = str_sql + ' and a.dt<=%s'
            str_count = str_count + ' and a.dt<=%s'
            qry_args.append(end_dt)
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


# 查询订单列表信息，支持条件查询
def get_pc(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    pc_id = js.get('pc_id', 0)
    gd_id = js.get('gd_id', 0)
    sp_id = js.get('sp_id', 0)
    em_id = js.get('em_id', 0)
    status = js.get('status', None)
    start_dt = js.get('start_dt', None)
    end_dt = js.get('end_dt', None)
    page_no = js.get('page_no', 0)
    page_size = js.get('page_size', 0)
    order_field = js.get('order_field', 'id')
    order = js.get('order', 'asc')
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        qry_args = []
        str_count = 'select count(a.id) from t_pc as a,t_good as b,t_em as c,t_supp as d where a.gd_id=b.id and ' \
                    'a.em_id=c.id and a.sp_id=d.id'
        str_sql = 'select a.*,b.name as gd_name,b.code as gd_code,b.gb as gd_gb,c.name as em_name,d.name as ' \
                  'sp_name from t_pc as a,t_good as b,t_em as c,t_supp as d where a.gd_id=b.id and ' \
                  'a.em_id=c.id and a.sp_id=d.id'
        if pc_id > 0:
            str_sql = str_sql + ' and a.id=%s'
            str_count = str_count + ' and a.id=%s'
            qry_args.append(pc_id)
        if gd_id > 0:
            str_sql = str_sql + ' and a.gd_id=%s'
            str_count = str_count + ' and a.id=%s'
            qry_args.append(gd_id)
        if sp_id > 0:
            str_sql = str_sql + ' and a.sp_id=%s'
            str_count = str_count + ' and a.id=%s'
            qry_args.append(sp_id)
        if em_id > 0:
            str_sql = str_sql + ' and a.em_id=%s'
            str_count = str_count + ' and a.id=%s'
            qry_args.append(em_id)
        if status:
            str_sql = str_sql + ' and a.status=%s'
            str_count = str_count + ' and a.id=%s'
            qry_args.append(status)
        if start_dt:
            str_sql = str_sql + ' and a.dt>=%s'
            str_count = str_count + ' and a.dt>=%s'
            qry_args.append(start_dt)
        if end_dt:
            str_sql = str_sql + ' and a.dt<=%s'
            str_count = str_count + ' and a.dt<=%s'
            qry_args.append(end_dt)
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


# 新增采购订单
def add_pc(js):
    """
    js = {'tenant': 'tk_huawei', 'gd_id': 2132, 'sp_id': 567, 'pc_count': 1000.0,
              'price': 12.34, 'remark': 'this is a test', 'em_id': 1}
    """
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    gd_id = js['gd_id']
    sp_id = js['sp_id']
    pc_count = js['pc_count']
    price = js['price']
    opt_id = js['opt_id']
    remark = js['remark']
    if pc_count < 0.0001:
        str_msg = '采购数量必须大于0'
        js_ret['err_msg'] = str_msg
        return js_ret
    if price < 0.0001:
        str_msg = '采购价格必须大于0'
        js_ret['err_msg'] = str_msg
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select id from t_supp where id=%s'
        cur.execute(str_sql, args=[sp_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '供货商%s不存在' % sp_id
            js_ret['err_msg'] = str_msg
            return js_ret
        str_sql = 'select id from t_good where id=%s'
        cur.execute(str_sql, args=[gd_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '物料%d不存在' % gd_id
            js_ret['err_msg'] = str_msg
            return js_ret
        pc_name = get_pc_name(tenant)
        str_sql = 'insert into t_pc(name,gd_id,em_id,sp_id,price,count,to_pay_amount,status,remark,pay_status) ' \
                  'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(str_sql,
                    args=[pc_name, gd_id, opt_id, sp_id, price, pc_count, pc_count * price, '待审核', remark, '待审核'])
        str_msg = '创建采购订单%s' % pc_name
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 采购订单审核
def approval_pc(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    pc_id = js['pc_id']
    approval_result = js['approval_result']
    opt_id = js['opt_id']
    audit_comments = js['audit_comments']
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select status from t_pc where id=%s'
        cur.execute(str_sql, args=[pc_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '订单%d不存在' % pc_id
            js_ret['err_msg'] = str_msg
            return js_ret
        if r[0] != '待审核':
            str_msg = '订单%d当前状态为%s，无法审核' % (pc_id, r[0])
            js_ret['err_msg'] = str_msg
            return js_ret
        str_sql = 'update t_pc set status=%s,audit_comments=%s,pay_status=%s where id=%s'
        if approval_result:  # 审核通过
            ap_args = ['待收货', audit_comments, '待支付', pc_id]
            str_msg = '订单[%d]审核通过，审核信息为[%s]' % (pc_id, audit_comments)
        else:  # 驳回
            ap_args = ['草稿', audit_comments, '待审核', pc_id]
            str_msg = '订单[%d]审核不通过，审核信息为[%s]' % (pc_id, audit_comments)
        cur.execute(str_sql, args=ap_args)
        write_log(str_msg, tenant=tenant)
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 修改订单信息（仅仅单价、数量、备注信息）
def edit_pc(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    pc_id = js['pc_id']
    pc_count = js['pc_count']
    price = js['price']
    opt_id = js['opt_id']
    remark = js.get('remark', '')
    if pc_count < 0.0001:
        str_msg = '采购数量必须大于0'
        js_ret['err_msg'] = str_msg
        return js_ret
    if price < 0.0001:
        str_msg = '采购价格必须大于0'
        js_ret['err_msg'] = str_msg
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select price,count,remark,status from t_pc where id=%s'
        cur.execute(str_sql, args=[pc_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '订单%d不存在' % pc_id
            js_ret['err_msg'] = str_msg
            return js_ret
        last_price = r[0]
        last_count = r[1]
        remark = r[2] + ',修改订单' + remark
        status = r[3]
        if status != '待审核':
            str_msg = '订单%d未处于待审核状态，无法修改单价和数量' % pc_id
            js_ret['err_msg'] = str_msg
            return js_ret
        str_sql = 'update t_pc set price=%s,count=%s,remark=%s where id=%s'
        ap_args = [price, pc_count, remark, pc_id]
        cur.execute(str_sql, args=ap_args)
        str_msg = '修改采购订单'
        if price != last_price:
            str_msg = str_msg + ',价格%.f->%.f' % (last_price, price)
        if pc_count != last_count:
            str_msg = str_msg + ',订货量%.f->%.f' % (last_count, pc_count)
        write_log(str_msg, tenant=tenant)
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 删除采购订单
def del_pc(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    pc_id = js['pc_id']
    opt_id = js['opt_id']
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select status,name from t_pc where id=%s'
        cur.execute(str_sql, args=[pc_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '订单%d不存在' % pc_id
            js_ret['err_msg'] = str_msg
            return js_ret
        status = r[0]
        pc_name = r[1]
        if status not in ['待审核', '草稿']:
            str_msg = '只能删除状态为待审核、草稿的订单，订单[%d/%s]无法删除' % (pc_id, pc_name)
            js_ret['err_msg'] = str_msg
            return js_ret
        str_sql = 'delete from t_pc where id=%s'
        cur.execute(str_sql, args=[pc_id])
        str_msg = '删除采购订单%d/%s' % (pc_id, pc_name)
        write_log(str_msg, tenant=tenant)
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 支付
def pay_pc(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    pc_id = js['pc_id']
    opt_id = js['opt_id']
    amount = js['amount']
    pay_finished = js.get('pay_finished', False)
    remark = js.get('remark', '')
    if amount < 0.001:
        str_msg = '支付金额必须大于0'
        js_ret['err_msg'] = str_msg
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select name,pay_status,price,count,paid_amount from t_pc where id=%s'
        cur.execute(str_sql, args=[pc_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '订单%d不存在' % pc_id
            js_ret['err_msg'] = str_msg
            return js_ret
        pc_name = r[0]
        pay_status = r[1]
        to_pay = r[2] * r[3] - r[4]  # 待支付金额
        if pay_status not in ['待支付', '支付中']:
            str_msg = '订单[%d/%s]未处于待支付或支付中状态，无法进行支付' % (pc_id, pc_name)
            js_ret['err_msg'] = str_msg
            return js_ret
        if amount >= to_pay:
            pay_finished = True
        pay_status = '支付中'
        if pay_finished:
            pay_status = '完成'
        str_sql = 'update t_pc set paid_amount=paid_amount+%s,pay_status=%s where id=%s'
        cur.execute(str_sql, args=[amount, pay_status, pc_id])
        str_sql = 'insert into t_pc_pay(pc_id,amount,em_id,remark) values(%s,%s,%s,%s)'
        cur.execute(str_sql, args=[pc_id, amount, opt_id, remark])
        str_msg = '支付采购订单%d/%s，金额%.2f' % (pc_id, pc_name, amount)
        write_log(str_msg, tenant=tenant)
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


# 退货
def return_pc(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    pc_id = js['pc_id']
    opt_id = js['opt_id']
    count = js['count']
    bc = js['bc']
    return_type = js['return_type']
    remark = js.get('remark', '')
    if count < 0.001:
        str_msg = '退货数量必须大于0'
        js_ret['err_msg'] = str_msg
        return js_ret
    cnn = None
    cur = None
    try:
        cnn = get_tenant_cnn(tenant)
        cur = cnn.cursor()
        str_sql = 'select name,rec_count,status from t_pc where id=%s'
        cur.execute(str_sql, args=[pc_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '订单%d不存在' % pc_id
            js_ret['err_msg'] = str_msg
            return js_ret
        pc_name = r[0]
        rec_count = r[1]
        status = r[2]
        if status not in ['待收货', '完成']:
            str_msg = '订单[%d/%s]未处于待收货或完成状态，无法退货' % (pc_id, pc_name)
            js_ret['err_msg'] = str_msg
            return js_ret
        if count > rec_count:
            str_msg = '订单[%d/%s]退货数量[%.2f]超过已到货数量[%.2f]，无法退货' % (pc_id, pc_name, count, rec_count)
            js_ret['err_msg'] = str_msg
            return js_ret
        str_sql = 'select sum(a.stock_count) from t_barcode as a,t_checkin as b where a.barcode=b.barcode ' \
                  'and b.pc_id=%s and a.barcode=%s'
        cur.execute(str_sql, args=[pc_id, bc])
        r = cur.fetchone()
        if r is None:
            str_msg = '订单%d的进货记录不包含%s批次信息，无法退货' % (pc_id, bc)
            js_ret['err_msg'] = str_msg
            return js_ret
        stock_count = r[0]
        if count > stock_count:  # 退货数量大于此批次的入库数量
            str_msg = '退货数量[%.2f]超过该批次[%s]的库存数量[%.2f]' % (count, bc, stock_count)
            js_ret['err_msg'] = str_msg
            return js_ret
        str_sql = 'update t_pc set rec_count=rec_count+%s where id=%s'
        cur.execute(str_sql, args=[count, pc_id])
        str_sql = 'insert into t_pc_return(pc_id,em_id,count,type,remark,barcode) values(%s,%s,%s,%s,%s,%s)'
        cur.execute(str_sql, args=[pc_id, opt_id, count, return_type, remark, bc])
        str_msg = '采购订单%d/%s退货%.2f，批次为%s' % (pc_id, pc_name, count, bc)
        write_log(str_msg, tenant=tenant)
        str_sql = 'insert into t_logs(em_id,op_content) values(%s,%s)'
        cur.execute(str_sql, args=[opt_id, str_msg])
        js_ret['result'] = True
        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    # js = {'tenant': 'tk_huawei', 'gd_id': 2132, 'sp_id': 567, 'pc_count': 5000.0,
    #       'price': 200, 'remark': 'this is a test', 'em_id': 1}
    # print(add_pc(js))
    # js = {'tenant': 'tk_huawei', 'pc_id': 1, 'approval_result': True, 'audit_comments': '赶紧让对方发货', 'em_id': 1}
    # print(approval_pc(js))
    # js = {'tenant': 'tk_huawei', 'pc_id': 2, 'price': 22.11, 'pc_count': 900, 'em_id': 1}
    # print(edit_pc(js))
    # js = {'tenant': 'tk_huawei', 'pc_id': 2}
    # print(get_pc(js))
    # js = {'tenant': 'tk_huawei', 'pc_id': 2, 'em_id': 1}
    # print(del_pc(js))
    # js = {'tenant': 'tk_huawei', 'pc_id': 1, 'em_id': 1, 'amount': 9999, 'pay_finished': True}
    # print(pay_pc(js))
    # js = {'tenant': 'tk_huawei', 'pc_id': 1, 'em_id': 1, 'count': 1, 'return_type': '质量不好', 'remark': '质量不好',
    #       'bc': 'bd_ddd'}
    # print(return_pc(js))
    js = {'tenant': 'tk_huawei'}
    print(get_pc_paid_info(js))


if __name__ == '__main__':
    main()
