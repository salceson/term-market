# -*- coding: utf-8 -*-

from __future__ import absolute_import
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from celery import task
from datetime import date, timedelta, datetime
import os
import re
import csv
from .models import Offer, Term, Teacher, Subject
from django.conf import settings
from django.db import transaction, IntegrityError

WEEKDAYS = dict(Pn=0, Wt=1, Sr=2, Cz=3, Pt=4, Sb=5, Nd=6)
DATE_PATTERN = re.compile(r'^(Pn|Wt|Sr|Cz|Pt|Sb|Nd) (0?[0-9]|1[0-9]|2[0-3]):'
                          r'([0-5]\d)\-(0?[0-9]|1[0-9]|2[0-3]):([0-5]\d)( [AB])?$', re.UNICODE)
DATE_MESSAGE = 'date must match format: <Pn|Wt|Sr|Cz|Pt|Sb|Nd> H[H]:MM-H[H]:MM[ <A|B>]'
STANDARD_STRING_PATTERN = re.compile(r'^[\w\-.:,; ]{,255}$', re.UNICODE)
STANDARD_STRING_FORMAT = '%s must be string with length at most 255'
STANDARD_INT_PATTERN = re.compile(r'^\d+$', re.UNICODE)
STANDARD_INT_FORMAT = '%s must be integer'
IMPORT_ERROR_FORMAT = 'Import error: line %d: %s.'


class TermsImportError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __unicode__(self):
        return self.message

    def __str__(self):
        return self.__unicode__()


class DateConverter(object):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    def convert_date(self, datestr, line):
        if not re.match(DATE_PATTERN, datestr):
            raise TermsImportError(IMPORT_ERROR_FORMAT % (line, DATE_MESSAGE))
        year = ''
        if datestr.endswith((' A', ' B')):
            year = datestr[-1:]
            datestr = datestr[:-2]
        weekday, hours = datestr.split(' ', 1)
        start_hour, end_hour = hours.split('-')
        day = self.week_start + timedelta(days=WEEKDAYS[weekday])
        start_hour = datetime.strptime(start_hour, '%H:%M').time()
        end_hour = datetime.strptime(end_hour, '%H:%M').time()
        start = datetime.combine(day, start_hour)
        end = datetime.combine(day, end_hour)
        return start, end, year


def check_string_fields(line, *args):
    for arg in args:
        val, par = arg
        if not re.match(STANDARD_STRING_PATTERN, unicode(val)):
            raise TermsImportError(IMPORT_ERROR_FORMAT % (line, STANDARD_STRING_FORMAT % par))


def check_int_fields(line, *args):
    for arg in args:
        val, par = arg
        if not re.match(STANDARD_INT_PATTERN, val):
            raise TermsImportError(IMPORT_ERROR_FORMAT % (line, STANDARD_INT_FORMAT % par))


@task()
def import_terms_task(filename, enrollment):
    if settings.DEBUG:
        print filename, enrollment
    date_converter = DateConverter()
    try:
        with transaction.atomic():
            try:
                Offer.objects.filter(offered_term__subject__enrollment=enrollment).delete()
                Term.objects.filter(subject__enrollment=enrollment).delete()
                reader = csv.DictReader(open(filename), delimiter='\t')
                i = 2
                for x in reader:
                    if settings.DEBUG:
                        print x['subject'], x['location'], x['date'], x['id'], x['group'], x['teacher']
                    start, end, year = date_converter.convert_date(x['date'], i)
                    teacher_last_name, teacher_first_name = x['teacher'].rsplit(' ', 1)
                    check_string_fields(i, (x['subject'], 'subject'), (x['location'], 'location'),
                                        (teacher_first_name, 'teacher first name'),
                                        (teacher_last_name, 'teacher last name'))
                    check_int_fields(i, (x['id'], 'id'))
                    try:
                        term = Term.objects.get(external_id=int(x['id']))
                    except Term.DoesNotExist:
                        term = Term()
                    teacher, teacher_created = Teacher.objects.get_or_create(first_name=teacher_first_name,
                                                                             last_name=teacher_last_name)
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
                    i += 1
            except TermsImportError as e:
                print e.message
                exc = IntegrityError()
                exc.message = e.message
                raise exc
    except IntegrityError as e:
        return False, e.message
    finally:
        os.remove(filename)
    return True, 'OK'
