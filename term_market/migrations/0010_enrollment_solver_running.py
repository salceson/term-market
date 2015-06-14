# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('term_market', '0009_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='solver_running',
            field=models.BooleanField(default=False, help_text=b"Can't touch this...",
                                      verbose_name=b'Indicates if the solver is running', editable=False),
        ),
    ]
