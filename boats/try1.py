import os
import time
from datetime import datetime

a = r"C:\\Users\\hardcase1\\PycharmProjects\\myproject\\media\\1559152711.923645.png"



def set_last_access_time(path):
    fileLocation = r"%s" % path
    year = 2017
    month = 11
    day = 5
    hour = 19
    minute = 50
    second = 0

    date = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    modTime = time.mktime(date.timetuple())

    os.utime(a.boat_photo.path, (datetime.now().timestamp(), datetime.now().timestamp()))
    print(os.path.getatime(fileLocation))
    print(datetime.now().timestamp())

set_last_access_time(a)
#print(os.path.getatime(a))
#print(datetime.now().timestamp())
