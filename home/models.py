from django.db import models


class Text(models.Model):
   id = models.IntegerField(primary_key=True)
   content = models.CharField(max_length=200)
   sender = models.IntegerField()
   receiver = models.IntegerField()
   datetime = models.DateTimeField(max_length=200)
   is_read = models.BooleanField(default=False)


class Email(models.Model):
   id = models.IntegerField(primary_key=True)
   sender = models.EmailField()
   receiver = models.EmailField()
   subject = models.CharField(max_length=200)
   content = models.CharField(max_length=1000*20) #300 words 20 characters per word
   datetime = models.DateTimeField(max_length=200)
