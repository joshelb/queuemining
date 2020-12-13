from django.db import models
from .validator import validate_file_extension


class TimeStep(models.Model):
    timeframe = models.IntegerField(default=1)
    unit = models.CharField(max_length=10)


class Data(models.Model):
    document = models.FileField(upload_to='documents/', validators=[validate_file_extension])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    timestep = models.ManyToManyField(TimeStep)
