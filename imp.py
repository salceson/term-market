# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import csv
from datetime import date, datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TermMarket.settings")

import django
django.setup()

from term_market.models import Enrollment, Subject, Teacher, Term

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

enrollment, created = Enrollment.objects.get_or_create(name='Testowe zapisy', external_id=1)
Term.objects.all().delete()

reader = csv.DictReader(open('terms.txt'), delimiter='\t')
for x in reader:
    print x['subject'], x['location'], x['date'], x['id'], x['group'], x['teacher']
    start, end, year = convert_date(x['date'])
    teacher_last_name, teacher_first_name = x['teacher'].rsplit(' ', 1)
    try:
        term = Term.objects.get(external_id=int(x['id']))
    except Term.DoesNotExist:
        term = Term()
    teacher, teacher_created = Teacher.objects.get_or_create(first_name=teacher_first_name, last_name=teacher_last_name)
    subject, subject_created = Subject.objects.get_or_create(name=x['subject'], enrollment=enrollment)
    term.teacher = teacher
    term.subject = subject
    term.start_time = start
    term.end_time = end
    term.week = year
    term.department_group = int(x['group']) if x['group'] != '' else 0
    term.room = x['location']
    term.external_id = int(x['id'])
    term.save()
