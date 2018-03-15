from django.db import models
import datetime
from django.contrib.auth.models import User
from . import etymology
import random


class Child(models.Model):
    parent_guardian = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date_of_birth = models.DateField(default=datetime.date.today)
    is_default = models.BooleanField()

    def __str__(self):
        default_char = ''
        if self.is_default:
            default_char = '(default)'
        return self.parent_guardian.username + ' : ' + self.name + ' ' + default_char

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

    def custom_save(self):
        other_children = Child.objects.filter(parent_guardian = self.parent_guardian)
        self.name = self.name.strip()

        # Checks to see if the parent-guardian has another child by the same
        # "friendly" (alphanumeric) name.
        for child in other_children:
            if self.url_friendly() == child.url_friendly() and child.id != self.id:
                return False

        #If the parent/guardian has no other registered children, register this
        #child as "default" for purposes of adding words.
        if len(other_children) == 0:
            self.is_default = True
        else:
            self.is_default = False

        self.save()
        return True

    #Makes this child the default child. Un-defaults any other child.
    def make_default(self):
        for child in self.parent_guardian.child_set.all():
            child.is_default = False
            child.save()
        self.is_default = True
        self.save()

    def get_vocabulary(self):
        words = self.word_set.all()
        if len(words) == 0:
            return False
        else:
            return words


class Word(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    word = models.CharField(max_length=50)
    date = models.DateField(default=datetime.date.today)
    etymology = models.TextField(default='', blank=True, null=True)
    note = models.CharField(max_length=500, blank=True, default="")

    def __str__(self):
        return str(self.child) + ". Word = " + self.word

    def set_etymology(self):
        self.etymology = etymology.get_etymology(self.word)

    def custom_save(self):
        self.word = self.word.lower().strip()
        current_vocab = Word.objects.filter(child = self.child)

        for w in current_vocab:
            if w.word == self.word:
                return False

        self.set_etymology()
        self.save()
        return True

    #TODO: Make this work!
    def age_at_acquisition(self):
        pass

    def has_notes(self):
        if self.note == "":
            return False
        else:
            return True


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
            try:
                v = self.owner.viewer_set.all()
            except:
                pass
            else:
                for dude in v:
                    if dude.viewer == self.viewer:
                        return False
        return True

    def custom_save(self):
        if self.is_valid():
            self.save()
            return True
        else:
            return False


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
    sender = models.CharField(max_length=30, default='admin')
    date = models.CharField(max_length=20)
    message = models.TextField()

    def __str__(self):
        return self.sender + ' -> ' + self.recipient.username + ': ' + self.message[:100] + '\t(' + self.date + ')'

    def is_valid(self):
        recip = User.objects.get(username=self.recipient)
        sender = User.objects.get(username=self.sender)
        pending_message = False
        blocked = False

        try:  # see if there are any messages from sender to recipient:
            msgs = recip.message_set.filter(sender=sender.username)[0]
        except:  # if not,
            pass
        else:  # if this triggers, then there is a pending request.
            pending_message = True

        try:
            senders_viewer_object = recip.viewer_set.filter(viewer=sender.username)[0]
        except:  # If sender does not have a viewer object associated with recipient, then recip is not blocked]
            pass
        else:  # Otherwise, need to check if sender is blocked by recip, or if recip has a pending msg from user.
            if senders_viewer_object.is_blocked:
                blocked = True

        message = ''
        if not blocked and not pending_message:
            return [True, 'Your message has been sent.']
        else:
            if blocked:
                message += 'You have been blocked by this user. Your message will not be processed. '
            if blocked and pending_message:
                message += '<br>'
            if pending_message:
                message += 'You have a pending friend request to this user. Your message will not be processed. '
            return [False, message]

    def is_actionable(self):
        if self.sender == 'admin' or self.recipient.username == 'admin':
            return False
        else:
            return True


def initiate_friendship(user1, user2):

    rel = check_relationship(user1, user2)

    if rel['error'] == True or rel['friendship'] == True or rel['block'] == True:
        return False

    v1 = Viewer()
    v1.owner = User.objects.get(username=user1)
    v1.viewer = user2
    v1.is_blocked = False
    if v1.custom_save() == True:
        v2 = Viewer()
        v2.owner = User.objects.get(username=user2)
        v2.viewer = user1
        v2.is_blocked = False
        if v2.custom_save() == True:
            return True
    return False


def initiate_block(blocker, blockee):

    rel = check_relationship(blocker, blockee)

    if rel['error'] == True:
        return False
    if rel['block'] == True:
        return False  # logic: If one user already blocks the other, that's enough to stop comms from going through.

    disintegrate_friendship(blocker, blockee)

    v = Viewer()
    v.owner = User.objects.get(username=blocker)
    v.viewer = blockee
    v.is_blocked = True
    if v.custom_save() == True:  # use custom_save to prevent duplicate viewer objects
        return True
    else:
        return False


def disintegrate_friendship(user1, user2):

    rel = check_relationship(user1, user2)

    if rel['error'] == True:
        return False

    user1 = User.objects.get(username=user1)
    user2 = User.objects.get(username=user2)

    try:
        v1 = user1.viewer_set.filter(viewer=user2.username)
        #print(v1)
    except:
        pass
    else:
        for v in v1:
            if v.is_blocked:
                pass
            else:
                v.delete()

    try:
        v2 = user2.viewer_set.filter(viewer=user1.username)
        #print(v2)
    except:
        pass
    else:
        for v in v2:
            if v.is_blocked:
                pass
            else:
                v.delete()
    return True


def check_relationship(user1, user2):
    d = dict()
    d['error'] = False
    d['friendship'] = False
    d['block'] = False

    two_way = 0

    try:
        user1 = User.objects.get(username=user1)
        user2 = User.objects.get(username=user2)
    except:
        d['error'] = True
        d['error_message'] = 'Invalid user(s).'
        return d

    d['block_details'] = ''

    try:
        v1 = user1.viewer_set.get(viewer=user2.username)
    except:
        pass
    else:
        if v1.is_blocked:
            d['block'] = True
            d['block_details'] += user1.username + ' blocks ' + user2.username + ' . '
        else:
            two_way += 1

    try:
        v2 = user2.viewer_set.get(viewer=user1.username)
    except:
        pass
    else:
        if v2.is_blocked:
            d['block'] = True
            d['block_details'] += user2.username + ' blocks ' + user1.username + '. '
        else:
            two_way += 1

    if d['block'] == True:
        d['friendship'] = False

    if d['block_details'] == '':
        del d['block_details']

    if two_way == 2:
        d['friendship'] = True

    d['error_message'] = False
    return d


def remove_block(blocker, blockee):
    rel = check_relationship(blocker, blockee)
    if rel['error'] == True:
        return False

    if rel['block'] == False:
        return False

    else:
        blocker = User.objects.get(username=blocker)
        v = blocker.viewer_set.filter(viewer=blockee)
        for relation in v:
            relation.delete()
    return True


#Gets the id of the child set as default for the given parent-guardian ID
#Returns False if there was an error or the child object if no error.
def get_default_child(parent_guardian_id):
    #If the id isn't matched to a user, return False
    try:
        parent_guardian = User.objects.get(id=parent_guardian_id)
    except:
        return (False, 'No parent/guardian with that id #')

    #If the PG has no children, return false.
    children = parent_guardian.child_set.all()
    if len(children) == 0:
        return False

    default_children = []
    for child in children:
        if child.is_default:
            default_children.append(child)

    #If there is more than one default child, set all children to is_default = False,
    #then choose a child at random to set as default. Return that child object.
    if len(default_children) > 1:
        for ch in children:
            ch.is_default = False
            ch.save()
        ch = random.choice(parent_guardian.child_set.all())
        ch.is_default = True
        ch.save()
        return ch

    #Otherwise, return the default child object.
    else:
        return default_children[0]
