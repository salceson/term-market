# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('term_market', '0005_auto_20150512_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='term',
            name='conflicting_terms',
            field=models.ManyToManyField(related_name='conflicting_terms_rel_+', to='term_market.Term'),
        ),
    ]
