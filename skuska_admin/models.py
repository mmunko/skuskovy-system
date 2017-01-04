from django.db import models

# Create your models here.
class Test(models.Model):
    test_nazov = models.CharField(max_length=200)
    test_subor = models.CharField(max_length=200)
    predmet = models.CharField(max_length=200)
    active = models.BooleanField(default=0)
    passwd = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return "{}: {}".format(self.predmet,self.test_nazov)
