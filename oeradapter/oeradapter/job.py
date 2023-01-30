from django_cron import CronJobBase, Schedule
from datetime import datetime

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'oeradapter.my_cron_job'  # a unique code

    def do(self):
        file = open("testsjob.txt", "w")
        file.write((datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        file.close()
