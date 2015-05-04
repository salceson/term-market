# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('term_market', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('external_id', models.BigIntegerField(help_text=b'ID of this enrollment in Enroll-me', null=True, verbose_name=b'External ID', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('external_id', models.BigIntegerField(help_text=b'ID of this subject in Enroll-me', null=True, verbose_name=b'External ID', blank=True)),
                ('enrollment', models.ForeignKey(to='term_market.Enrollment')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=32)),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('week', models.CharField(blank=True, max_length=1, choices=[(b'', b'all'), (b'A', b'week A'), (b'B', b'week B')])),
                ('room', models.CharField(max_length=16)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('department_group', models.PositiveSmallIntegerField()),
                ('external_id', models.BigIntegerField(help_text=b'ID of this term in Enroll-me', null=True, verbose_name=b'External ID', blank=True)),
                ('subject', models.ForeignKey(to='term_market.Subject')),
                ('teacher', models.ForeignKey(to='term_market.Teacher')),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='internal_id',
            field=models.CharField(null=True, max_length=20, blank=True, help_text=b'Used to match OAuth external user to their TermMarket user account.', unique=True, verbose_name=b'Internal ID'),
        ),
        migrations.AlterField(
            model_name='user',
            name='transcript_no',
            field=models.CharField(max_length=6, null=True, verbose_name=b'Transcript number', blank=True),
        ),
    ]
