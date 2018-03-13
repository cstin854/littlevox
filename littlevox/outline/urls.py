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
    url(r'^user/(?P<user>[A-Za-z0-9]+)/$', views.user_splashpage, name='user_splashpage'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^register/$', views.register, name='register'),
    url(r'^itemlist/$', views.blank_item_list, name='itemlist'),
    url(r'^childlist/$', views.all_child_list, name='allchildlist'),
    url(r'^users/', views.users, name='users'),
    url(r'^addword/', views.addword, name='addword'),
    url(r'^process_message/', views.process_message, name='process_message'),
    url(r'^addword/', views.addword, name='addword'),
    url(r'^addchild/', views.addchild, name='addchild'),
    url(r'^(?P<user>[A-Za-z0-9]+)/child/(?P<childname>[A-Za-z0-9]+)/', views.child_dashboard, name='child_dashboard'),
    url(r'^(?P<user>[A-Za-z0-9]+)/child/(?P<childname>[A-Za-z0-9]+)/word/child/(?P<word>[A-Za-z0-9]+)/', views.child_word, name='child_word'),
    url(r'^rm/(?P<user>[A-Za-z0-9]+)/', views.remove_viewer, name='remove_viewer'),
    url(r'^blocked_users/', views.blocked_users, name='blocked_users'),
    url(r'^unblock/(?P<user_to_unblock>[A-Za-z0-9]+)/', views.unblock, name='unblock'),
    url(r'^frrq/(?P<recipient>[A-Za-z0-9]+)/', views.friend_request, name='friend_request'),
]
