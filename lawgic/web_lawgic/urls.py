from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('files/', views.list_files, name='list_files'),
    path('download/<str:folder>/<str:filename>/', views.download_file, name='download_file'),
]
