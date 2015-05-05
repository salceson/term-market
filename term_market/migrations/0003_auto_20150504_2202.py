# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('term_market', '0002_auto_20150504_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='term',
            name='students',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='first_name',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='title',
            field=models.CharField(max_length=32, blank=True),
        ),
        migrations.AlterField(
            model_name='term',
            name='department_group',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='internal_id',
            field=models.CharField(help_text=b'Used to match OAuth external user to their TermMarket user account.', max_length=20, null=True, verbose_name=b'Internal ID', blank=True),
        ),
    ]
