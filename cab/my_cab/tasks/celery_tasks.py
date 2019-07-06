from celery import Celery
from my_cab.libs.ronglianyun.SendTemplateSMS import CCP


celery_app = Celery("my_cab", broker="redis://127.0.0.1:6379/8")


@celery_app.task
def send_sms(to, data, temp_id):
    ccp = CCP()
    ccp.send_template_sms(to, data, temp_id)

