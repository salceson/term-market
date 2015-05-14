# coding=utf-8

from __future__ import absolute_import
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from celery import task
from datetime import date, timedelta, datetime
import os
import csv
from .models import Offer, Term, Teacher, Subject

WEEKDAYS = dict(Pn=0, Wt=1, Sr=2, Cz=3, Pt=4, Sb=5, Nd=6)


class DateConverter(object):
    TODAY = date.today()
    WEEK_START = TODAY - timedelta(days=TODAY.weekday())

    def convert_date(self, datestr):
        year = ''
        if datestr.endswith((' A', ' B')):
            year = datestr[-1:]
            datestr = datestr[:-2]
        weekday, hours = datestr.split(' ', 1)
        start_hour, end_hour = hours.split('-')
        day = self.WEEK_START + timedelta(days=WEEKDAYS[weekday])
        start_hour = datetime.strptime(start_hour, '%H:%M').time()
        end_hour = datetime.strptime(end_hour, '%H:%M').time()
        start = datetime.combine(day, start_hour)
        end = datetime.combine(day, end_hour)
        return start, end, year


@task()
def import_terms_task(filename, enrollment):
    print filename, enrollment
    date_converter = DateConverter()
    try:
        Offer.objects.filter(enrollment=enrollment).delete()
        Term.objects.filter(enrollment=enrollment).delete()
        reader = csv.DictReader(open('terms.txt'), delimiter='\t')
        for x in reader:
            print x['subject'], x['location'], x['date'], x['id'], x['group'], x['teacher']
            start, end, year = date_converter.convert_date(x['date'])
            teacher_last_name, teacher_first_name = x['teacher'].rsplit(' ', 1)
            try:
                term = Term.objects.get(external_id=int(x['id']))
            except Term.DoesNotExist:
                term = Term()
            teacher, teacher_created = Teacher.objects.get_or_create(first_name=teacher_first_name,
                                                                     last_name=teacher_last_name)
            subject, subject_created = Subject.objects.get_or_create(name=x['subject'], enrollment=enrollment)
            term.teacher = teacher
            term.enrollment = enrollment
            term.subject = subject
            term.start_time = start
            term.end_time = end
            term.week = year
            term.department_group = int(x['group']) if x['group'] != '' else 0
            term.room = x['location']
            term.external_id = int(x['id'])
            term.save()
    except:
        return False
    finally:
        os.remove(filename)
    return True
