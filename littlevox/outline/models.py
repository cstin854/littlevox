from django.db import models
import datetime
from django.contrib.auth.models import User

# Create your models here.

class Child(models.Model):
    parent_guardian = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date_of_birth = models.DateField(default=datetime.date.today)