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
        item.text = 'Date of birth: '+str(self.date_of_birth)+'<br>'
        item.text += 'Parent-guardian: '
        item.text += '<a href="/outline/user/'+str(self.parent_guardian.username)+'/"' + \
                     '>'+\
                     str(self.parent_guardian.username)+'</a>'
        # url to send for splashpage for that child
        item.link = '/' + str(self.parent_guardian) + '/' + str(self.name) + '/'
        item.link_text = str(self.name)+"'s Dashboard"
        return item

    def url_friendly(self):
        val = ''
        for char in self.name:
            if char.lower() in 'qwertyuiopasdfghjklzxcvbnm':
                val += char.lower()
            elif char in '0123456789':
                val += char
        return val


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
    viewer = models.CharField(max_length=30)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        ch = ''
        if self.is_blocked:
            ch += ' (X)'
        return str(self.owner.username)+' : '+self.viewer + ch

    def is_valid(self):  # returns a Boolean to determine if the viewer matches with a valid user.
        try:
            u = User.objects.get(username=self.viewer)
        except:
            return False
        else:
            return True

    def recriprocate(self):
        if self.is_valid and self.is_blocked is False:
            owner = User.objects.get(username=self.viewer)
            viewer = User.objects.get(username=self.owner)
            v = Viewer()
            v.owner = owner
            v.viewer = viewer.username
            v.is_blocked = False

class ItemListObject():

    def __init__(self, title=False, imgsrc=False, text=False, link=False, link_text='Click for details.'):
        self.title = title
        self.imgsrc = imgsrc
        self.text = text
        self.link = link
        self.link_text = link_text

    def has_content(self):
        if self.title == False and self.imgsrc == False and self.text == False:
            return False
        else:
            return True


class Message(models.Model):

    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.CharField(max_length=30)
    date = models.CharField(max_length=20)
    message = models.TextField()

    def __str__(self):
        return self.sender + ' -> ' + self.recipient.username + ': ' + self.message[:100] + '\t(' + self.date + ')'

    def is_valid(self):
        return True
