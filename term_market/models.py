from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    transcript_no = models.CharField('Transcript number', max_length=6, blank=True, null=True)
    internal_id = models.CharField('Internal ID',
                                   help_text='Used to match OAuth external user to their TermMarket user account.',
                                   max_length=20, blank=True, null=True)


class Enrollment(models.Model):
    name = models.CharField(max_length=64)
    external_id = models.BigIntegerField('External ID', help_text='ID of this enrollment in Enroll-me', blank=True,
                                         null=True)

    def __unicode__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=64)
    enrollment = models.ForeignKey('Enrollment')
    external_id = models.BigIntegerField('External ID', help_text='ID of this subject in Enroll-me', blank=True,
                                         null=True)

    def __unicode__(self):
        return self.name


class Teacher(models.Model):
    title = models.CharField(max_length=32, blank=True)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.title + ' ' + self.first_name + ' ' + self.last_name


WEEK_CHOICES = (
    ('', 'all'),
    ('A', 'week A'),
    ('B', 'week B')
)


class Term(models.Model):
    subject = models.ForeignKey('Subject')
    teacher = models.ForeignKey('Teacher')
    week = models.CharField(max_length=1, choices=WEEK_CHOICES, blank=True)
    room = models.CharField(max_length=16)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    department_group = models.PositiveSmallIntegerField(blank=True, null=True)
    external_id = models.BigIntegerField('External ID', help_text='ID of this term in Enroll-me', blank=True, null=True)
    students = models.ManyToManyField('User', related_name='terms')

    def __unicode__(self):
        return unicode(self.subject) + ' - ' + self.start_time.strftime('%a, %H:%M') + ' ' + unicode(self.week) + \
            ' - ' + unicode(self.teacher)


class Offer(models.Model):
    offered_term = models.ForeignKey('Term')
    wanted_terms = models.ManyToManyField('Term', related_name='offers')
    donor = models.ForeignKey('User', related_name='donated')
    bait = models.CharField(max_length=255, blank=True)
    is_available = models.BooleanField(default=True)
