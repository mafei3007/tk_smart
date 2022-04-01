# -*- coding: utf-8 -*-

"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-23 10:53
@Desc   ：
==================================================
"""

import json
import time
import traceback
from flask import Flask, request, g, redirect
from flask_login import login_user, login_required, logout_user, current_user
from tk_util import write_log

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=False)
