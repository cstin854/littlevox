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
    url(r'^user/(?P<user>[A-Za-z0-9]+)/$', views.user_splashpage, name='user_splashpage'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^register/$', views.register, name='register'),
    url(r'^users/', views.users, name='users'),
    url(r'^addword/', views.addword, name='addword'),
    url(r'^process_message/', views.process_message, name='process_message'),
    url(r'^addword/', views.addword, name='addword'),
    url(r'^addchild/', views.addchild, name='addchild'),
    url(r'^child/(?P<childid>[0-9]+)/', views.child_dashboard, name='child_dashboard'),
    url(r'^word/edit/(?P<wordid>[0-9]+)/', views.edit_word, name='edit_word'),
    url(r'^word/(?P<wordid>[A-Za-z0-9]+)/', views.child_word, name='child_word'),
    url(r'^rm/(?P<user>[A-Za-z0-9]+)/', views.remove_viewer, name='remove_viewer'),
    url(r'^rmword/(?P<wordid>[0-9]+)/', views.remove_word, name='remove_word'),
    url(r'^rmword_confirm/(?P<wordid>[0-9]+)/', views.remove_word_execute, name='remove_word_execute'),
    url(r'^rmchild/(?P<childid>[0-9]+)/', views.remove_child, name='remove_child'),
    url(r'^blocked_users/', views.blocked_users, name='blocked_users'),
    url(r'^unblock/(?P<user_to_unblock>[A-Za-z0-9]+)/', views.unblock, name='unblock'),
    url(r'^frrq/(?P<recipient>[A-Za-z0-9]+)/', views.friend_request, name='friend_request'),
]
