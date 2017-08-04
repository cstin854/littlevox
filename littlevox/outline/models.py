from django.db import models
import datetime
from django.contrib.auth.models import User
from . import etymology


class Child(models.Model):
    parent_guardian = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date_of_birth = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.parent_guardian.username + ' : ' + self.name

    def as_itemlist_item(self):
        item = ItemListObject()
        item.title = str(self.name)
        item.imgsrc = False
        item.text = 'Date of birth: '+str(self.date_of_birth)
        # url to send for splashpage for that child
        item.link = '/' + str(self.parent_guardian) + '/' + str(self.name) + '/'
        item.link_text = str(self.name)+"'s Dashboard"
        return item


class Word(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    word = models.CharField(max_length=50)
    date = models.DateField(default=datetime.date.today)
    etymology = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return str(self.child) + ". Word = " + self.word

    def set_etymology(self):
        self.etymology = etymology.get_etymology(self.word)


# Probably not the best way to do this, but this class provides a way for a user
# to determine the users that will be able to view her content. Default is ';public;'
# Usage (when "username" is logged in, trying to access content owned by "owner":
#   if ';'+username+';' in Viewers.objects.filter(owner="owner").viewers
# Something like the above. Will need to tweak in practice!


class Viewer(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    viewer = models.CharField(max_length=50)

    def __str__(self):
        return str(self.owner.username)+' : '+self.viewer


class ItemListObject():

    def __init__(self, title=False, imgsrc=False, text=False, link=False, link_text='Click for details.'):
        self.title = title
        self.imgsrc = imgsrc
        self.text = text
        self.link = link
        self.link_text = link_text
        if title == False and imgsrc == False and text == False:
            self.has_content = False
        else:
            self.has_content = True
