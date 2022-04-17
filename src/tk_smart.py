# -*- coding: utf-8 -*-

"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-23 10:53
@Desc   ：
==================================================
"""

import time
import traceback
from flask import Flask, request, g, redirect
from flask_login import login_required, logout_user  # , current_user,login_user,
from tk_util import write_log
from process.tk_em import get_em, add_em, edit_em, del_em
from process.tk_cust import get_cust, add_cust, edit_cust, del_cust
from process.tk_good import get_gd, add_gd, edit_gd, del_gd
from process.tk_role import get_role, add_role, edit_role, del_role
from process.tk_sp import get_sp, add_sp, edit_sp, del_sp
from process.tk_wp import get_wp, add_wp, edit_wp, del_wp
from process.tk_ws import get_ws, add_ws, edit_ws, del_ws
from process.tk_unit import get_unit, add_unit, edit_unit, del_unit
from process.tk_stock import get_stock, add_stock, edit_stock, del_stock
from process.tk_ext_type import get_ext_type, add_ext_type, edit_ext_type, del_ext_type
from process.tk_ext import get_ext, add_ext, edit_ext, del_ext
from process.tk_em_rl import get_em_role, edit_role

__author__ = 'MaFei'

app = Flask(__name__)


@app.before_request
def before_request():
    g.start = time.time()


@app.after_request
def aft_request(response):
    url = request.url
    method = request.method
    status = response.status_code
    t_span = time.time() - g.start
    str_req = request.json
    str_resp = response.json
    s_msg = '%s,%s[%.2fs],%d request=%s, response=%s' % (url, method, t_span, status, str_req, str_resp)
    write_log(s_msg)
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    err_msg = traceback.format_exc()
    js_resp = dict()
    status = e.code
    js_resp['err_code'] = e.code
    js_resp['err_name'] = e.name
    js_resp['err_msg'] = err_msg
    js_resp['err_desc'] = e.description
    print(js_resp)
    return js_resp, status


@app.route('/login', methods=['POST'])
def login():
    # https://www.shuzhiduo.com/A/ZOJPrq9ydv/
    js_req = request.json if request.data else {}
    # login_user(user, form.remember_me.data)
    return js_req, 200


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/api/<tenant_id>/test', methods=['GET', 'POST'])
def prt_cmd(tenant_id):
    js_req = request.json if request.data else {}
    print(tenant_id)
    return js_req, 200


@app.route('/api/<tenant_id>/get_em', methods=['GET'])
def f_get_em(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_em(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/add_em', methods=['POST'])
def f_add_em(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = add_em(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_em', methods=['POST'])
def f_edit_em(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_em(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/del_em', methods=['POST'])
def f_del_em(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = del_em(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/get_cust', methods=['GET'])
def f_get_cust(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_cust(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/add_cust', methods=['POST'])
def f_add_cust(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = add_cust(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_cust', methods=['POST'])
def f_edit_cust(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_cust(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/del_cust', methods=['POST'])
def f_del_cust(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = del_cust(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/get_gd', methods=['GET'])
def f_get_gd(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_gd(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/add_gd', methods=['POST'])
def f_add_gd(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = add_gd(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_gd', methods=['POST'])
def f_edit_gd(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_gd(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/del_gd', methods=['POST'])
def f_del_gd(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = del_gd(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/get_role', methods=['GET'])
def f_get_role(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_role(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/add_role', methods=['POST'])
def f_add_role(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = add_role(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_role', methods=['POST'])
def f_edit_role(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_role(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/del_role', methods=['POST'])
def f_del_role(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = del_role(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/get_sp', methods=['GET'])
def f_get_sp(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_sp(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/add_sp', methods=['POST'])
def f_add_sp(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = add_sp(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_sp', methods=['POST'])
def f_edit_sp(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_sp(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/del_sp', methods=['POST'])
def f_del_sp(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = del_sp(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/get_wp', methods=['GET'])
def f_get_wp(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_wp(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/add_wp', methods=['POST'])
def f_add_wp(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = add_wp(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_wp', methods=['POST'])
def f_edit_wp(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_wp(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/del_wp', methods=['POST'])
def f_del_wp(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = del_wp(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/get_ws', methods=['GET'])
def f_get_ws(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_ws(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/add_ws', methods=['POST'])
def f_add_ws(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = add_ws(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_ws', methods=['POST'])
def f_edit_ws(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_ws(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/del_ws', methods=['POST'])
def f_del_ws(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = del_ws(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/get_unit', methods=['GET'])
def f_get_unit(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_unit(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/add_unit', methods=['POST'])
def f_add_unit(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = add_unit(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_unit', methods=['POST'])
def f_edit_unit(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_unit(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/del_unit', methods=['POST'])
def f_del_unit(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = del_unit(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/get_stock', methods=['GET'])
def f_get_stock(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_stock(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/add_stock', methods=['POST'])
def f_add_stock(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = add_stock(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_stock', methods=['POST'])
def f_edit_stock(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_stock(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/del_stock', methods=['POST'])
def f_del_stock(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = del_stock(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/get_ext_type', methods=['GET'])
def f_get_ext_type(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_ext_type(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/add_ext_type', methods=['POST'])
def f_add_ext_type(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = add_ext_type(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_ext_type', methods=['POST'])
def f_edit_ext_type(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_ext_type(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/del_ext_type', methods=['POST'])
def f_del_ext_type(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = del_ext_type(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/get_ext', methods=['GET'])
def f_get_ext(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_ext(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/add_ext', methods=['POST'])
def f_add_ext(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = add_ext(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_ext', methods=['POST'])
def f_edit_ext(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_ext(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/del_ext', methods=['POST'])
def f_del_ext(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = del_ext(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/get_em_role', methods=['GET'])
def f_get_em_role(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = get_em_role(js_req)
    status = 200
    return js_resp, status


@app.route('/api/<tenant_id>/edit_role', methods=['POST'])
def f_edit_role(tenant_id):
    js_req = request.json if request.data else {}
    js_req['tenant'] = tenant_id
    js_resp = edit_role(js_req)
    status = 200
    return js_resp, status


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=False)
