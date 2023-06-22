from datetime import datetime
import pytz

date_format = '%Y/%m/%d'
date_time_format = '%Y/%m/%d %H:%M:%S'


def getDateStr(date):
    return date.strftime(date_time_format)

def getCurrentDateAndTime():
    # return datetime.now(pytz.timezone("Asia/Kolkata"))
    return datetime.now()

def getDateTime(time):
    # today_date = datetime.now(pytz.timezone("Asia/Kolkata")).strftime(date_format)
    today_date = datetime.now().strftime(date_format)
    date_time = datetime.strptime(today_date+" "+time+":00", date_time_format)
    return date_time
