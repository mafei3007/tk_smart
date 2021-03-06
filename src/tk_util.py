# -*-coding:utf-8-*-

"""
=================================================
@Project   ： tk_smart
@Author ：   Ma fei
@Date   ：   2022-03-23 10:53
@Desc   ：   工具类
==================================================
"""
import binascii
import json
import re
import socket
import traceback
import uuid

import httplib2
import os
import time
import smtplib
import qrcode
from email.mime.text import MIMEText
from pyDes import des, CBC, PAD_PKCS5
from pathlib import Path
from constant import des_secret_key, from_email, from_email_pwd, default_pwd


def get_host():
    my_name = socket.getfqdn(socket.gethostname())
    my_address = socket.gethostbyname(my_name)
    return my_address


def get_curr():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def free_obj(obj):
    if obj is None:
        return
    try:
        obj.close()
    except Exception as em:
        str_err = '释放对象异常:%s' % repr(em).split('(')[0]
        write_log(str_err)


def des_encrypt(str_input):
    iv = des_secret_key
    k = des(des_secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(str_input, padmode=PAD_PKCS5)
    by_hex = binascii.b2a_hex(en)
    return bytes.decode(by_hex)


def des_decrypt(str_input):
    iv = des_secret_key
    k = des(des_secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(binascii.a2b_hex(str_input), padmode=PAD_PKCS5)
    return bytes.decode(de)


# 判断字符串只能由数字、26个英文字母或者下划线组成
def check_field_name(field_name):
    if field_name is None:
        return '不能为空'
    if len(field_name.strip()) == 0:
        return '长度不能为空'
    if len(field_name) > 64:
        return '长度不能超过64'
    pattern = re.compile(r'[0-9a-zA-Z_]+$')
    if not pattern.findall(field_name):
        return '只能由数字、26个英文字母或者下划线组成'
    return None


# 校验密码复杂度是否符合要求
def check_pwd(pwd):
    if pwd is None:
        return '密码不能为空'
    if len(pwd.strip()) == 0:
        return '密码长度不能为空'
    if len(pwd) < 9:
        return '密码长度不能小于8'
    if pwd.lower() == default_pwd.lower():
        return '不能使用默认密码'
    pattern = re.compile('[0-9]+')
    if not pattern.findall(pwd):
        return '密码不能都是数字'
    pattern = re.compile('[A-Za-z]')
    if not pattern.findall(pwd):
        return '密码不能都是字母'
    pattern = re.compile(r'\d')
    if not pattern.findall(pwd):
        return '密码必须要包含至少一个数字'
    pattern = re.compile('[A-Z]+')
    if not pattern.findall(pwd):
        return '密码必须包含至少一个大写字母'
    pattern = re.compile('[a-z]+')
    if not pattern.findall(pwd):
        return '密码必须包含至少一个小写字母'
    pattern = re.compile('^[a-z0-9A-Z]+')
    if not pattern.findall(pwd):
        return '密码必须要以数字或字母开头'
    return None


def send_message(url, method='GET', js_body=None, js_header=None):
    status = 404
    js_resp = dict()
    if js_header:
        js_header = {'Content-type': 'application/json'}
    try:
        http_obj = httplib2.Http(timeout=30)  # 默认超时30秒
        response, content = http_obj.request(url, method=method, headers=js_header,
                                             body=json.dumps(js_body, ensure_ascii=True))
        status = response.status
        js_resp = json.loads(content)
        print(json.dumps(js_resp, indent=4))
    except Exception as em:
        err_msg = '%s,详细异常:%s.' % (repr(em), traceback.format_exc())
        js_resp['err_msg'] = err_msg
    return status, js_resp


def send_email(to_addr, subject='默认主题', content=''):
    from_addr = from_email
    password = from_email_pwd
    if len(from_addr) == 0 or len(password) == 0:
        str_msg = '未配置发件人邮箱或密码，无法发送邮件'
        write_log(str_msg)
        return False
    msg = MIMEText(content, 'txt', 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    smtp = None
    try:
        smtp = smtplib.SMTP_SSL('smtp.163.com', 465)
        smtp.ehlo("smtp.163.com")
        smtp.login(from_addr, password)
        smtp.sendmail(from_addr, [to_addr], msg.as_string())
    finally:
        if smtp:
            smtp.close()
    return True


def write_log(str_msg, tenant=None):
    # dir_log = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'logs'
    dir_log = r'D:\py_workspace\tk_smart\logs'
    if not Path(dir_log).exists():
        os.mkdir(dir_log)
    if tenant:
        log_file = dir_log + os.sep + time.strftime('%Y%m%d', time.localtime(time.time())) + '_' + tenant + '.log'
    else:
        log_file = dir_log + os.sep + time.strftime('%Y%m%d', time.localtime(time.time())) + '.log'
    str_log = '%s %s\n' % (get_curr(), str_msg)
    try:
        with open(log_file, 'a', encoding='utf8') as f:
            f.write(str_log)
    except Exception as em:
        str_err = '%s,详细异常:%s.' % (repr(em), traceback.format_exc())
        print(str_err)


def write_db_log(str_sql, args=None, tenant=None):
    # dir_log = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'logs'
    dir_log = r'D:\py_workspace\tk_smart\logs'
    if not Path(dir_log).exists():
        os.mkdir(dir_log)
    if tenant:
        log_file = dir_log + os.sep + time.strftime('%Y%m%d', time.localtime(time.time())) + '_' + tenant + '_db.log'
    else:
        log_file = dir_log + os.sep + time.strftime('%Y%m%d', time.localtime(time.time())) + '_db.log'
    if args:
        str_log = '%s SQL:%s,Param:%s\n' % (get_curr(), str_sql, str(args))
    else:
        str_log = '%s SQL:%s,Param:Null\n' % (get_curr(), str_sql)
    try:
        with open(log_file, 'a', encoding='utf8') as f:
            f.write(str_log)
    except Exception as em:
        str_err = '%s,详细异常:%s.' % (repr(em), traceback.format_exc())
        print(str_err)


def get_bc_img(bc_content):
    # version参数----二维码的格子矩阵大小，可以是1到40，1最小为21*21，40是177*177
    # error_correction参数----二维码错误容许率，默认ERROR_CORRECT_M，容许小于15%的错误率
    # box_size参数----二维码每个小格子包含的像素数量
    # border参数----二维码到图片边框的小格子数，默认值为4
    img_res = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'img_res'
    if not Path(img_res).exists():
        os.mkdir(img_res)
    img_res = img_res + os.sep + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    if not Path(img_res).exists():
        os.mkdir(img_res)
    img_file = img_res + os.sep + str(uuid.uuid4()) + '.bmp'
    if os.path.exists(img_file):
        os.remove(img_file)
    img = qrcode.make(bc_content, version=4, box_size=20, border=2)
    img.save(img_file)
    return img_file


# 判断对象是否都为空
def is_none(lst_o):
    if lst_o is None:
        return True
    if not isinstance(lst_o, list):
        return True
    for o in lst_o:
        if o:
            return False
    return True


def is_not_none(lst_o):
    if lst_o is None:
        return False
    if not isinstance(lst_o, list):
        return True
    for o in lst_o:
        if o is None:
            return False
    return True


def main():
    # url = 'http://192.168.1.5:5005/login'
    # method = 'GET'
    # js_body = {'user': '马飞', 'code': 'hero'}
    # js_head = {'user-id': 'mafei', 'tenant_id': 'tk_huawei'}
    url = 'http://192.168.1.5:5005/api/tk_huawei/qry_em'
    method = 'GET'
    js_body = {'page_no': 1, 'page_size': 20}
    js_head = {'user': 'mafei', 'tenant_id': 'tk_huawei'}
    print(send_message(url, method=method, js_body=js_body, js_header=js_head))
    # print(des_encrypt('gj12345'))
    # print(des_decrypt('21f6f4abe215bbf466c57fb50403ff42'))
    # send_email('mafeihong123@126.com', subject='邮件主题', content='This is a test memo.')
    # pwd = 'te1st'
    # pattern = re.compile(r'\d')
    # if not pattern.findall(pwd):
    #     print('密码必须要包含至少一个数字')


def sjt():
    i = 10
    while True:
        i += 1
        val = i * i * i + 4 * i * i
        print('实话实说：这种我都做不出来%d ----%d' % (i, val))
        if i > 30:
            break


if __name__ == '__main__':
    sjt()
