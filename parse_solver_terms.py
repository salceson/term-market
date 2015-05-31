# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TermMarket.settings")

import django
django.setup()

from term_market.models import Enrollment

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

from ConfigParser import SafeConfigParser

terms_parser = SafeConfigParser(allow_no_value=True)
terms_parser.read(os.path.join('sample-data', 'solver_terms.txt'))

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
