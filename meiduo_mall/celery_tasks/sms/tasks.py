# 生产者 -- 任务/函数
# 1. 这个函数 必须要让celery的实例对象 task装饰器装饰
# 2. 需要celery 自动监测指定包的任务

from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

@app.task
def celery_send_sms_code(mobile, code, expire, template_id):
    CCP().send_template_sms(mobile, [code, expire], template_id)