from django.db import models
from .validator import validate_file_extension


class Document(models.Model):
    document = models.FileField(upload_to='documents/', validators=[validate_file_extension] )
    uploaded_at = models.DateTimeField(auto_now_add=True)
