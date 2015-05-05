# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('term_market', '0003_auto_20150504_2202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bait', models.CharField(max_length=255, blank=True)),
                ('donor', models.ForeignKey(related_name='donated', to=settings.AUTH_USER_MODEL)),
                ('recipient', models.ForeignKey(related_name='received', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='term',
            name='students',
            field=models.ManyToManyField(related_name='terms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='offer',
            name='term',
            field=models.ForeignKey(to='term_market.Term'),
        ),
    ]
