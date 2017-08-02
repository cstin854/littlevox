"""littlevox URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views

app_name = 'outline'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^word_test/', views.word_test, name='word_test'),
    url(r'^user/(?P<user>[A-Za-z0-9]+)/$', views.user_junk, name='user_junk'),
    url(r'^register/$', views.UserFormView.as_view(), name='register'),
    url(r'^register_test/$', views.register_test, name='register_test'),
    url(r'^itemlist/$', views.itemlist, name='itemlist'),
]
