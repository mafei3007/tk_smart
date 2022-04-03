# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-30 08:30
@Desc   ：人员角色分配
==================================================
"""
import datetime
from tk_util import write_log, free_obj
from db.comm_cnn import CommonCnn


# 查询人员角色信息
def get_em_role(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['len'] = -1
    js_ret['data'] = list()
    tenant = js['tenant']
    em_id = js['em_id']
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select a.id,a.name,a.remark from t_role as a,t_em_role as b where a.id=b.rl_id and b.em_id=%s'
        cur.execute(str_sql, args=[em_id])
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
        #cnn.close()


# 更新人员角色信息
def edit_unit(js):
    js_ret = dict()
    js_ret['err_msg'] = ''
    js_ret['result'] = False
    tenant = js['tenant']
    em_id = js['id']
    lst_rl_id = js.get('role_list', [])
    cnn = None
    cur = None
    try:
        cnn = CommonCnn().cnn_pool[tenant].connection()
        cur = cnn.cursor()
        str_sql = 'select name from t_em where id=%s'
        cur.execute(str_sql, args=[em_id])
        r = cur.fetchone()
        if r is None:
            str_msg = '%s人员不存在，无法编辑' % em_id
            js_ret['err_msg'] = str_msg
            write_log(str_msg, tenant=tenant)
            return js_ret
        em_name = r[0]
        str_sql = 'delete from t_em_role where em_id=%s'
        cur.execute(str_sql, args=[em_id])
        rl_names = ''
        for rl_id in lst_rl_id:
            str_sql = 'select name from t_role where id=%s'
            cur.execute(str_sql, args=[rl_id])
            r = cur.fetchone()
            if r:
                rl_names = rl_names + ' ' + r[0]
                str_sql = 'insert into t_em_rl(em_id,rl_id) values(%s,%s)'
                cur.execute(str_sql, args=[em_id, rl_id])
            else:
                str_msg = '%s角色不存在，无法更新用户角色信息' % rl_id
                write_log(str_msg, tenant=tenant)
        str_msg = '更新用户%s的角色->%s，该角色权限重新登录后生效' % (em_name, rl_names)
        write_log(str_msg, tenant=tenant)
        js_ret['result'] = True

        return js_ret
    finally:
        free_obj(cur)
        cnn.close()


def main():
    js = {'tenant': 'tk_huawei', 'em_id': 1}
    print(get_em_role(js))


if __name__ == '__main__':
    main()
