# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import colorful.fields


class Migration(migrations.Migration):

    dependencies = [
        ('term_market', '0007_auto_20150602_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='color',
            field=colorful.fields.RGBColorField(blank=True),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='solver_time',
            field=models.IntegerField(default=60, help_text=b"In minutes, doesn't matter if you don't use solver; 0 means running the solver manually", verbose_name=b'Time between solver runs', blank=True),
        ),
    ]
