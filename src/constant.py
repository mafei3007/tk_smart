# -*- coding: UTF-8 -*-
"""
=================================================
@Project   ： tk_smart
@Author ：Ma fei
@Date   ：2022-03-28 08:20
@Desc   ：公共常量类
==================================================
"""
comm_db_name = 'tk_smart_base'  # 主数据库名称
comm_db_user = 'root'  # 账户名
comm_db_pwd = '123'  # 密码
comm_db_host = '127.0.0.1'  # DB服务器IP
comm_db_charset = 'utf8'  # 字符集

# 单位类型枚举
comm_unit_type = ['数量', '重量', '容量', '面积', '长度', '自定义']

# 系统默认角色，不能修改
comm_role = ['超级用户', '仓库管理', '订单下发', '订单审核', '财务', '生产', '销售', '采购']

# 默认扩展类型代号
comm_def_ext_code = ['bc', 'len']

# 扩展类型代号不能使用如下字符串 202204101902 马飞
comm_invalid_ext_code = ['id', 'gd_id', 'stock_count', 'dt']

company_name = 'company_name'

company_bank = 'company_bank'

company_account = 'company_account'

company_credit_code = 'company_credit_code'

company_address = 'company_address'

pc_idx = 'PC'  # 采购订单编号前缀

so_idx = 'SO'  # 销售订单编号前缀

prod_idx = 'PROD'  # 生产工单名称前缀

of_idx = 'OF'  # 询价单名称前缀

account_delay_day = 'account_delay_day'  # 账期宽限天数

contract_validity = 'contract_validity'  # 合同有效期（年)

free_maintenance_year = 'free_maintenance_year'  # 免费维保年限

maintenance_year = 'maintenance_year'  # 维保年限

# 默认密码
default_pwd = 'Admin123'  # 必须要符合复杂度要求：字母或数字开头，必须包含至少数字和大小写字母，不能是纯数字或纯字母，且长度不小于8

# 密码加解密 密钥
des_secret_key = '12345678'

from_email = '13951623007@163.com'

from_email_pwd = 'fh@123.com'

# 每次更新或者添加BOM信息时，是否需要批量更新该产品所有相关实例的BOM配置
update_all_good_bom = True
