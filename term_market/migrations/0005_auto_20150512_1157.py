# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('term_market', '0004_auto_20150505_0002'),
    ]

    operations = [
        migrations.RenameField(
            model_name='offer',
            old_name='term',
            new_name='offered_term',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='recipient',
        ),
        migrations.AddField(
            model_name='offer',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='offer',
            name='wanted_terms',
            field=models.ManyToManyField(related_name='offers', to='term_market.Term'),
        ),
    ]
