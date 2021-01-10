from django.db import models
from .validator import validate_file_extension


class TimeStep(models.Model):
    timeframe = models.IntegerField(default=1)
    unit = models.CharField(max_length=10)

    def __str__(self):
        if self.unit == "H":
            output = str(self.timeframe) + " Hour(s)"
        elif self.unit == "D":
            output = str(self.timeframe) + " Day(s)"
        elif self.unit == "W":
            output = str(self.timeframe) + " Week(s)"
        elif self.unit == "M":
            output = str(self.timeframe) + " Month(s)"
        return output


class Data(models.Model):
    document = models.FileField(upload_to='documents/', validators=[validate_file_extension])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    timestep = models.ManyToManyField(TimeStep)
    current = models.IntegerField(default=1)
