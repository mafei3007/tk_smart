# -*-coding:utf-8-*-

"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-23 10:53
@Desc   ：
==================================================
"""
import binascii
import json
import re
import socket
import traceback
import httplib2
import os
import time
import smtplib
import qrcode
from email.mime.text import MIMEText
from pyDes import des, CBC, PAD_PKCS5
from pathlib import Path
from constant import des_secret_key, from_email, from_email_pwd


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


# 校验密码复杂度是否符合要求
def check_pwd(pwd):
    if pwd is None:
        return '密码不能为空'
    if len(pwd.strip()) == 0:
        return '密码长度不能为空'
    if len(pwd) < 9:
        return '密码长度不能小于8'
    pattern = re.compile('[0-9]+')
    if not pattern.findall(pwd):
        return '密码不能都是数字，必须包含数字，大小写字母'
    pattern = re.compile('[A-Z]+')
    if not pattern.findall(pwd):
        return '密码必须包含大写字母，必须包含数字，大小写字母'
    pattern = re.compile('[a-z]+')
    if not pattern.findall(pwd):
        return '密码必须包含小写字母，必须包含数字，大小写字母'
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


def get_bc_img(bc_content):
    # version参数----二维码的格子矩阵大小，可以是1到40，1最小为21*21，40是177*177
    # error_correction参数----二维码错误容许率，默认ERROR_CORRECT_M，容许小于15%的错误率
    # box_size参数----二维码每个小格子包含的像素数量
    # border参数----二维码到图片边框的小格子数，默认值为4
    img_res = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'img_res'
    if not Path(img_res).exists():
        os.mkdir(img_res)
    img_file = time.strftime('%Y%m%d%H%M%S_', time.localtime(time.time())) + str(uuid.uuid4()) + '.bmp'
    img_file = img_res + os.sep + img_file
    if os.path.exists(img_file):
        os.remove(img_file)
    img = qrcode.make(bc_content, version=4, box_size=20, border=2)
    img.save(img_file)
    return img_file


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
    # js_bd = {'user': '马飞', 'code': 'hero'}
    # js_hd = {'user-id': 'mafei', 'tenant_id': 'tk_huawei'}
    # print(send_message(url, method=method, js_body=js_bd, js_header=js_hd))
    print(des_encrypt('gj12345'))
    print(des_decrypt('21f6f4abe215bbf466c57fb50403ff42'))
    # send_email('mafeihong123@126.com', subject='邮件主题', content='This is a test memo.')


if __name__ == '__main__':
    main()
