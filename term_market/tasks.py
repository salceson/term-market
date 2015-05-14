# coding=utf-8

from __future__ import absolute_import

from celery import task


@task()
def import_terms_task(filename, enrollment):
    print filename, enrollment
    return "pisiont"
