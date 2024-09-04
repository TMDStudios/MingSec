from django.db import models
from time import time, localtime, strftime

# Create your models here.

class CamRequest(models.Model):
    type = models.CharField(max_length=64, null=False)
    camera = models.CharField(max_length=64, null=False)
    length = models.SmallIntegerField(null=True)
    time = models.BigIntegerField(default=int(time()*1000))
    ip = models.CharField(max_length=64, null=True)

    def save(self, *args, **kwargs):
        self.time = int(time()*1000)
        super(CamRequest, self).save(*args, **kwargs)

class AlarmReport(models.Model):
    camera = models.CharField(max_length=64, null=False)
    time = models.CharField(max_length=64, null=True)

    def save(self, *args, **kwargs):
        self.time = strftime("%m-%d-%Y %H:%M:%S", localtime())
        super(AlarmReport, self).save(*args, **kwargs)

class StatusReport(models.Model):
    camera = models.CharField(max_length=64, null=False)
    status = models.CharField(max_length=255, null=False)
    time = models.CharField(max_length=64, null=True)

    def save(self, *args, **kwargs):
        self.time = strftime("%m-%d-%Y %H:%M:%S", localtime())
        super(StatusReport, self).save(*args, **kwargs)