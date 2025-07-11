from django.db import models

# Create your models here.

class Profile(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField(max_length=250)
  # User --< Cat
#   user = models.ForeignKey(User, on_delete=models.CASCADE)

class Guild(models.Model):
  name = models.CharField(max_length=50)
  description = models.TextField(max_length=250)
#   members = 
