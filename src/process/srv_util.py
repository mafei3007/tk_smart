# -*- coding: UTF-8 -*-


"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-23 10:53
@Desc   ：
==================================================
"""
import uuid
import base64
import os
import time
import qrcode
from pathlib import Path

g_tenant = 'tk_huawei'


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


# 加密 解密
def get_pwd(s, encode=True):
    if encode:  # 加密
        s = s + '*13dc%'
        str_ret = base64.b64encode(s.encode())
    else:  # 解密
        str_ret = base64.b64decode(s).decode()
        str_ret = str_ret[:-6]
    return str_ret


def main():
    qry_cond = {'op_content': '登录系统', 'em_id': 77, 'tb_name': 't_logs', 'page_no': 1, 'page_size': 10,
                'start_dt': '2020-07-01 00:00:00', 'end_dt': '2020-08-30 00:00:00'}
    print(qry_cond)


if __name__ == '__main__':
    main()
