from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from .forms import *


class Login(View):
    def get(self, request):
        form = AuthenticationForm()
        # signup_form = UserCreationForm()
        return render(request, 'shared_photo_library/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        signup_form = UserCreationForm()
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            print("user  logged in")
            return redirect('shared_photo_library:my_profile')
        return render(request, 'shared_photo_library/login.html', {'form': form})


class SignUp(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'shared_photo_library/signup.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shared_photo_library:login')
        return render(request, 'shared_photo_library/signup.html', {'form': form})


class Home(View):
    def get(self, request):
        return render(request, 'shared_photo_library/home.html')


class UploadPhoto(LoginRequiredMixin, View):
    def post(self, request):
        new_photo = Photo.objects.create()
        form = AddPhoto(request.POST, request.FILES, instance=new_photo)
        if form.is_valid():
            form.save()
            return redirect('shared_photo_library:upload_photo')

    def get(self, request):
        form = AddPhoto()
        return render(request, "shared_photo_library/upload_photo.html", {'form': form})


class MyProfile(View):
    def get(self, request):
        logged_in_user = request.user
        photos = list(Photo.objects.all())
        tags = list()
        for photo in photos:
            tags.append(list(photo.tags.all()))
        return render(request, 'shared_photo_library/my_profile.html',
                      {'user': logged_in_user, 'photos_and_tags': zip(photos, tags)})


