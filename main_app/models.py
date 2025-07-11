import datetime
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField(max_length=250)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

class Guild(models.Model):
  name = models.CharField(max_length=50)
  description = models.TextField(max_length=250)
#   members = 
