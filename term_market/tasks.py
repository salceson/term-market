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
from .models import Offer, Term, Teacher, Subject, User
from django.conf import settings
from django.db import transaction, IntegrityError

WEEKDAYS = dict(Pn=0, Wt=1, Sr=2, Cz=3, Pt=4, Sb=5, Nd=6)
DATE_PATTERN = re.compile(r'^(Pn|Wt|Sr|Cz|Pt|Sb|Nd) (0?[0-9]|1[0-9]|2[0-3]):'
                          r'([0-5]\d)\-(0?[0-9]|1[0-9]|2[0-3]):([0-5]\d)( [AB])?$', re.UNICODE)
DATE_MESSAGE = 'date must match format: <Pn|Wt|Sr|Cz|Pt|Sb|Nd> H[H]:MM-H[H]:MM[ <A|B>]'
STRING_FORMAT = '%s must be string with length at most 255'
INT_FORMAT = '%s must be integer'
INT_OR_EMPTY_FORMAT = INT_FORMAT + ' or empty'
IMPORT_ERROR_FORMAT = 'Import error: line %d: %s.'
STANDARD_ERROR = 'wrong file format'


class AbstractImportError(Exception):
    def __init__(self, line, msg):
        self.message = IMPORT_ERROR_FORMAT % (line, msg)

    def __unicode__(self):
        return self.message

    def __str__(self):
        return self.__unicode__()


class TermsImportError(AbstractImportError):
    pass


class DepartmentListImportError(AbstractImportError):
    pass


class DateConverter(object):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    def convert_date(self, datestr, line):
        if not re.match(DATE_PATTERN, datestr):
            raise TermsImportError(line, DATE_MESSAGE)
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


def check_string_fields_length(line, *args):
    for arg in args:
        val, par = arg
        if len(val) > 255:
            raise TermsImportError(line, STRING_FORMAT % par)


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
                line = 2
                for x in reader:
                    if settings.DEBUG:
                        print x['subject'], x['location'], x['date'], x['id'], x['group'], x['teacher']
                    start, end, year = date_converter.convert_date(x['date'], line)
                    teacher_last_name, teacher_first_name = x['teacher'].rsplit(' ', 1)
                    check_string_fields_length(line, (x['subject'], 'subject'), (x['location'], 'location'),
                                               (teacher_first_name, 'teacher first name'),
                                               (teacher_last_name, 'teacher last name'))
                    try:
                        term = Term.objects.get(external_id=int(x['id']))
                    except Term.DoesNotExist:
                        term = Term()
                    except ValueError:
                        raise TermsImportError(line, INT_FORMAT % 'id')
                    teacher, teacher_created = Teacher.objects.get_or_create(first_name=teacher_first_name,
                                                                             last_name=teacher_last_name)
                    subject, subject_created = Subject.objects.get_or_create(name=x['subject'], enrollment=enrollment)
                    term.teacher = teacher
                    term.subject = subject
                    term.start_time = start
                    term.end_time = end
                    term.week = year
                    try:
                        term.department_group = int(x['group']) if x['group'] != '' else 0
                    except ValueError:
                        raise TermsImportError(line, INT_OR_EMPTY_FORMAT % 'group')
                    term.room = x['location']
                    term.external_id = int(x['id'])
                    term.save()
                    line += 1
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


@task()
def import_department_list_task(filename, enrollment):
    try:
        with open(filename, 'r') as f:
            with transaction.atomic():
                try:
                    user = None
                    line_no = 1
                    for line in f:
                        line = line.rstrip()
                        if not line.startswith('\t\t'):
                            try:
                                name, enroll_id = line.split(';', 1)
                                last_name, first_name = name.split(' ', 1)
                            except ValueError:
                                raise DepartmentListImportError(line_no, STANDARD_ERROR)
                            try:
                                user = User.objects.get(transcript_no=enroll_id)
                            except User.DoesNotExist:
                                user = User()
                                user.username = '!ENROLL!' + enroll_id
                                user.first_name = first_name
                                user.last_name = last_name
                                user.transcript_no = enroll_id
                                user.save()
                            line_no += 1
                            continue
                        line = line.lstrip()
                        try:
                            subject, department_group = line.split(' - Grupa - ')
                        except ValueError:
                            raise DepartmentListImportError(line_no, STANDARD_ERROR)
                        subject = Subject.objects.get(name=subject, enrollment=enrollment)
                        term = Term.objects.get(subject=subject, department_group=int(department_group))
                        term.students.add(user)
                        print user, term
                        line_no += 1
                except DepartmentListImportError as e:
                    print e.message
                    exc = IntegrityError()
                    exc.message = e.message
                    raise exc
    except IntegrityError as e:
        return False, e.message
    finally:
        os.remove(filename)
    return True, 'OK'