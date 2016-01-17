from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from jsonfield import JSONField
from skuska_admin.models import Test

# Create your models here.

class Result(models.Model):
    student = models.CharField(max_length=200)
    test = models.ForeignKey(Test)
    otazky = models.CharField(max_length=500)
    odpovede = JSONField()
    body = models.SmallIntegerField()
    znamka = models.CharField(max_length=20,default='Fx')
    casova_peciatka = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '{} | {} | {}'.format(self.casova_peciatka.strftime('%Y-%m-%y %H:%M'),self.test.test_nazov,self.student)
