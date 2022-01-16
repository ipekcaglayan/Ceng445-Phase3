from django.contrib import admin
from django.urls import path
from .views import Login, Home, SignUp, UploadPhoto, MyProfile, PhotoView, CollectionView, CollectionDetail, FilterView

app_name = 'shared_photo_library'

urlpatterns = [
    path('', Home.as_view(), name="home"),
    path('login', Login.as_view(), name="login"),
    path('sign-up', SignUp.as_view(), name="signup"),
    path('upload-photo', UploadPhoto.as_view(), name="upload_photo"),
    path('my-profile', MyProfile.as_view(), name="my_profile"),
    path('photo', PhotoView.as_view(), name="update_photo"),
    path('photos', PhotoView.as_view(), name="photos"),
    path('collections', CollectionView.as_view(), name="collections"),
    path('collection/<int:id>', CollectionDetail.as_view(), name="collection_detail"),
    path('views', FilterView.as_view(), name="views"),

]
