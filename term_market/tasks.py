# -*- coding: utf-8 -*-

from __future__ import absolute_import
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from celery import task
from ConfigParser import SafeConfigParser
import csv
from datetime import date, timedelta, datetime
from django.db import transaction, IntegrityError, OperationalError
from django.conf import settings
from django.http import JsonResponse
import os
import re
from .models import Offer, Term, Teacher, Subject, User
from .offers_solver.solver import Solver

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


class ConflictsImportError(AbstractImportError):
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


@task()
def import_conflicts_task(filename, enrollment):
    try:
        with transaction.atomic():
            terms_parser = SafeConfigParser(allow_no_value=True)
            terms_parser.read(filename)

            enrollment_terms = Term.objects.filter(subject__enrollment=enrollment).all()
            for term in enrollment_terms:
                term.conflicting_terms.clear()

            terms = {}
            for subject in enrollment.subject_set.all():
                for term in subject.term_set.all():
                    terms[term.external_id] = term

            for subj_id in terms_parser.sections():
                if subj_id == 'kolizje':
                    for pair, _ in terms_parser.items(subj_id):
                        term1, term2 = pair.split(';', 1)

                        subj1_id, term1_id = term1.split(',')
                        subj1_id, term1_id = int(subj1_id), int(term1_id)
                        if not terms[term1_id].subject.external_id:
                            terms[term1_id].subject.external_id = subj1_id
                            terms[term1_id].subject.save()

                        subj2_id, term2_id = term2.split(',')
                        subj2_id, term2_id = int(subj2_id), int(term2_id)
                        if not terms[term2_id].subject.external_id:
                            terms[term2_id].subject.external_id = subj2_id
                            terms[term2_id].subject.save()

                        terms[term1_id].conflicting_terms.add(terms[term2_id])
                        terms[term2_id].conflicting_terms.add(terms[term1_id])
    except IntegrityError as e:
        return False, e.message
    finally:
        os.remove(filename)
    return True, 'OK'


@task()
def delete_file(filename):
    os.remove(filename)
    return True


@task()
def run_solver(enrollment, offers_file, conflicts_file, output_file):
    print 'Enrollment', enrollment.id
    enrollment.solver_running = True
    enrollment.save()
    results = []
    try:
        solver = Solver(offers_file, conflicts_file, output_file)
        solver.solve()
        with open(output_file) as f:
            for line in f:
                results.append(line)
        print results
    except Exception as e:
        return False, e.message
    finally:
        enrollment.solver_running = False
        enrollment.save()
        os.remove(offers_file)
        os.remove(conflicts_file)
        os.remove(output_file)
    return True, str(len(results)) + ' offers has been found!'


def task_check(task, error_msg):
    if not task:
        return JsonResponse(
            {'status': 'error', 'finished': False, 'success': False, 'message': 'Wrong task id'}
        )
    task_result = None
    try:
        task_result = import_terms_task.AsyncResult(task)
        finished = task_result.ready()
    except OperationalError:
        finished = False
    if finished and task_result.status == 'SUCCESS':
        success, message = task_result.get()
    else:
        success = False
        message = error_msg if finished else ''
    return JsonResponse(
        {'status': 'ok', 'finished': finished, 'success': success, 'message': message}
    )
