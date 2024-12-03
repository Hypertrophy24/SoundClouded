from django.urls import path

from .views import  HomePageView,play, index,callback, index,save_playlist,favicon

urlpatterns = [
    path("", play, name="home"),
    path('', index, name='index'),
   path('callback/', callback, name="callback"),
   path('index/',index, name="index"),
    path('save_playlist/', save_playlist, name='save_playlist'),
    path('play/', play, name='play'),
     path('favicon.ico', favicon),
]