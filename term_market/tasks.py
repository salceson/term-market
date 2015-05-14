# coding=utf-8

from __future__ import absolute_import
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from celery import task
from datetime import date, timedelta, datetime
import os

WEEKDAYS = dict(Pn=0, Wt=1, Sr=2, Cz=3, Pt=4, Sb=5, Nd=6)
TODAY = date.today()
WEEK_START = TODAY - timedelta(days=TODAY.weekday())


def convert_date(datestr):
    year = ''
    if datestr.endswith((' A', ' B')):
        year = datestr[-1:]
        datestr = datestr[:-2]
    weekday, hours = datestr.split(' ', 1)
    start_hour, end_hour = hours.split('-')
    day = WEEK_START + timedelta(days=WEEKDAYS[weekday])
    start_hour = datetime.strptime(start_hour, '%H:%M').time()
    end_hour = datetime.strptime(end_hour, '%H:%M').time()
    start = datetime.combine(day, start_hour)
    end = datetime.combine(day, end_hour)
    return start, end, year


@task()
def import_terms_task(filename, enrollment):
    print filename, enrollment
    # TODO: REALLY IMPORT THE FILE
    os.remove(filename)
    return True
