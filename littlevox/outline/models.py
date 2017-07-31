from django.db import models
import datetime
from django.contrib.auth.models import User

# Create your models here.

class Child(models.Model):
    parent_guardian = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date_of_birth = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.parent_guardian.username + ' : ' + self.name

class Word(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    word = models.CharField(max_length=50)
    date = models.DateField(default=datetime.date.today)
    etymology = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return str(self.child) + ". Word = " + self.word