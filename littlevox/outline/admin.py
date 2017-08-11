from django.contrib import admin
from .models import Child, Word, Viewer, Message

admin.site.register(Child)
admin.site.register(Word)
admin.site.register(Viewer)
admin.site.register(Message)