from datetime import datetime


def my_scheduled_job():
    file = open("testsjob.txt", "w")
    file.write((datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
    file.close()
