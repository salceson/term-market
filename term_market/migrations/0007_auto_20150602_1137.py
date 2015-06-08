# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('term_market', '0006_term_conflicting_terms'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='solver_time',
            field=models.IntegerField(default=60, help_text=b"In minutes, doesn't matter if you don't use solver",
                                      verbose_name=b'Time between solver runs', blank=True),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='solver_use',
            field=models.BooleanField(default=True, help_text=b'Using the epic solver',
                                      verbose_name=b'Run solver automatically'),
        ),
        migrations.AlterField(
            model_name='term',
            name='conflicting_terms',
            field=models.ManyToManyField(related_name='conflicting_terms_rel_+', to='term_market.Term', blank=True),
        ),
        migrations.AlterField(
            model_name='term',
            name='students',
            field=models.ManyToManyField(related_name='terms', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
