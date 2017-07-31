from django.shortcuts import render
from django.http import HttpResponse
from .models import Word

# Create your views here.

def index(request):
    return HttpResponse("<h1>Hello world!</h1>")

def word_test(request):
    html = ''
    words = Word.objects.all()
    for word in words:
        html += '<br><h1>Word: '+ str(word.word) +'</h1>'
        html += '<br><h3>Date: ' + str(word.date) + '</h3>'
        html += '<br>Etymology: ' + str(word.etymology)
    return HttpResponse(html)
