from django.db import models
from .validator import validate_file_extension


class DataFrame(models.Model):
    act_id = models.IntegerField(default=0)
    case_amount = models.DecimalField(max_digits=20, decimal_places=10)
    act_name = models.CharField(default="Activity", max_length=400)
    service_time = models.DecimalField(max_digits=20, decimal_places=10)
    waiting_time = models.DecimalField(max_digits=20, decimal_places=10)
    res_nr = models.DecimalField(max_digits=20, decimal_places=10)
    capacity = models.DecimalField(max_digits=20, decimal_places=10)


class TimeStep(models.Model):
    timeframe = models.IntegerField(default=1)
    unit = models.CharField(max_length=10)
    frame = models.ManyToManyField(DataFrame)

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
    offdays = models.CharField(default="7", max_length=100)
    day_start = models.IntegerField(default=1)
    day_end = models.IntegerField(default=1)
    timestep = models.ManyToManyField(TimeStep)
