from django.urls import path

from .views import  HomePageView,play, index


urlpatterns = [
    path("", play, name="home"),
    path('', index, name='index'),
    path('play/', play, name='play'),
]