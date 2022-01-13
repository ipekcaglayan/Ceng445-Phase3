from django.contrib import admin
from django.urls import path
from .views import Login, Home, SignUp

app_name = 'shared_photo_library'

urlpatterns = [
    path('', Login.as_view(), name="login"),
    path('home', Home.as_view(), name="home"),
    path('sign-up', SignUp.as_view(), name="signup"),
]
