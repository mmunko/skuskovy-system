from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from jsonfield import JSONField

# Create your models here.

class Result(models.Model):
    student = models.CharField(max_length=200)
    test_nazov = models.CharField(max_length=200)
    test_subor = models.TextField()
    odpovede = JSONField()
    body = models.SmallIntegerField()
    znamka = models.CharField(max_length=2,default='Fx')
    casova_peciatka = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '{} | {} | {}'.format(self.test_nazov,self.student,self.casova_peciatka)
