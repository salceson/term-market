# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('term_market', '0005_auto_20150512_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='enrollment',
            field=models.ForeignKey(default=1, to='term_market.Enrollment'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='term',
            name='enrollment',
            field=models.ForeignKey(default=1, to='term_market.Enrollment'),
            preserve_default=False,
        ),
    ]
