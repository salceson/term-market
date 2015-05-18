# -*- coding: utf-8 -*-
from itertools import groupby
from operator import attrgetter

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TermMarket.settings")

import django
django.setup()

from term_market.models import User, Enrollment, Term, TermStudent

enrollments = list(Enrollment.objects.all())
print 'Available enrollments:'
for i, enrollment in enumerate(enrollments, 1):
    print '%d) %s' % (i, enrollment)

while True:
    selected = raw_input('Which one to export? ')
    try:
        enrollment = enrollments[int(selected) - 1]
        break
    except Exception:
        print 'Bad choice, try again'

terms = Term.objects.filter(subject__enrollment=enrollment)
mapping = TermStudent.objects.filter(term__in=terms).order_by('user', 'term__subject')

for student, assignments in groupby(mapping, attrgetter('user')):
    print '[%s]' % student.transcript_no
    for assignment in assignments:
        print '%d:%d' % (assignment.term.subject.external_id, assignment.term.external_id)