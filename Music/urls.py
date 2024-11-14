from django.urls import path

from .views import  HomePageView,play, index
app_name = 'music'
urlpatterns = [
    path("home/", HomePageView.as_view(), name="home"),
    path('', index, name='index'),
    
    path('play/', play, name='play'),
]