from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path('features/', views.features, name='features'),
    path('community/', views.community, name='community'),
    path('contact/', views.contact, name='contact'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chat/', views.chat, name='chat'),
    path('files/', views.list_files, name='list_files'),
    path('download/<str:folder>/<str:filename>/', views.download_file, name='download_file'),
    path('about/', views.about, name='about'),
    path('chat_history/', views.chat_history, name='chat_history'),
]
