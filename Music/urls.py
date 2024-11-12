from django.urls import path

from .views import  play, index, callback

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path('', index, name='index'),
    path('callback/', callback, name='callback'),
    path('play/', play, name='play'),
]