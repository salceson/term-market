# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('term_market', '0011_bugreports'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bugreports',
            name='message',
            field=models.CharField(max_length=255, verbose_name=b'message'),
        ),
    ]
