from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.


class Photo(models.Model):
    photo = models.ImageField(blank=True)
    location = models.CharField(max_length=100, null=True)
    date = models.DateTimeField(default=timezone.now, null=True)
    tags = models.CharField(max_length=100, null=True)


class FilterView(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='view_owner')
    view_name = models.CharField(max_length=100)
    shared_users = models.ManyToManyField(User, related_name='view_shared_with')
    tags = models.CharField(max_length=100, null=True)
    conjunctive = models.BooleanField(default=False)
    login_required = models.BooleanField(default=True)
    location_rect = models.CharField(max_length=100, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)


class Collection(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='col_owner')
    collection_name = models.CharField(max_length=100)
    shared_users = models.ManyToManyField(User, related_name='col_shared_with')
    views = models.ManyToManyField(FilterView)
