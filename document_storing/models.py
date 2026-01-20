from django.db import models
from django.contrib.auth.models import User

class FileInfo(models.Model):
    path = models.URLField()
    info = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.path