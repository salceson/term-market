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

from term_market.models import Enrollment, Subject, Teacher, Term, User

enrollment = Enrollment.objects.get(name='Testowe zapisy', external_id=1)

user = None
with open('department-list.csv', 'r') as f:
    for line in f:
        line = line.rstrip()
        if not line.startswith('\t\t'):
            name, enroll_id = line.split(';', 1)
            last_name, first_name = name.split(' ', 1)
            try:
                user = User.objects.get(transcript_no=enroll_id)
            except User.DoesNotExist:
                user = User()
                user.username = '!ENROLL!' + enroll_id
                user.first_name = first_name
                user.last_name = last_name
                user.transcript_no = enroll_id
                user.save()
            continue
        line = line.lstrip()
        subject, department_group = line.split(' - Grupa - ')
        subject = Subject.objects.get(name=subject, enrollment=enrollment)
        term = Term.objects.get(subject=subject, department_group=int(department_group))
        term.students.add(user)
        print user, term
