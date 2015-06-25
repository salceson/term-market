# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('term_market', '0012_auto_20150625_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='bugreports',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 25, 19, 14, 11, 357097, tzinfo=utc), verbose_name=b'date'),
            preserve_default=False,
        ),
    ]
