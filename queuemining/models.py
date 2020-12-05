from django.db import models
from .validator import validate_file_extension


class Table(models.Model):
    UNIT_CHOICES = (
        ("N", "---"),
        ("H", "Hour"),
        ("D", "Day"),
        ("W", "Week"),
        ("M", "Month")
    )
    document = models.FileField(upload_to='documents/', validators=[validate_file_extension] )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    timeframe = models.IntegerField(default=1)
    unit = models.ChoiceField(label='unit', choices = UNIT_CHOICES)
