# -*- coding: utf-8 -*-


"""
执行命令：
uwsgi --socket 47.97.124.22:8089 -L --socket-timeout 60 --http -l 24 --protocol=http --threads 2 -w wsgi:hg_app
uwsgi --socket 47.97.124.22:8089 -L -l 24 --protocol=http --threads 2 -w wsgi:hg_app
--socket 10.43.35.210:5000：需要修改为实际的IP和端口号
--pyargv "10.43.35.210 5000 0" ：需要修改为实际的IP和端口号，最后一个参数，如果是功能测试则填写0，如果是性能测试，则填写1
--threads 2 ：线程数，性能测试中有可能会涉及到，一般用于性能微调用，默认2
--socket-timeout 60: socket超时，建议至少60秒
--http-timeout 60: http 超时
使用前建议了解一下wsgi的核心配置：http://heipark.iteye.com/blog/1847421
"""

if __name__ == "__main__":
    print('a')
