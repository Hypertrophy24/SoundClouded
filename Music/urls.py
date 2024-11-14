from django.urls import path

from .views import  HomePageView,play, index
app_name = 'music'
urlpatterns = [
    path("", play, name="home"),
    path('', index, name='index'),
    path("logout/", HomePageView.as_view(), name="account_logout"),
    path("login/", HomePageView.as_view(), name="account_login"),
    path('play/', play, name='play'),
]