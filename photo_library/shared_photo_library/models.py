from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from exif import Image
# Create your models here.
import datetime


class Photo(models.Model):
    photo = models.ImageField(blank=True)
    location = models.CharField(max_length=100, null=True)
    date = models.DateTimeField(null=True)
    tags = models.CharField(max_length=100, null=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    added_time = models.DateTimeField(default=timezone.now)

    def load_meta_data(self):
        img = Image(self.photo.open(mode='rb'))  # open img in binary mode to get meta data using exif
        self.tags = ""
        self.location = ""
        if img.has_exif:
            date = img.get('datetime')
            if date:
                dates = date.split(" ")
                yymmdd = [int(x) for x in dates[0].split(":")]
                saat = [int(x) for x in dates[1].split(":")]
                self.date = datetime.datetime(*(yymmdd + saat))
                print(self.date, "date")

            latitude = img.get('gps_latitude')
            longitude = img.get('gps_longitude')

            # if gps info exists, set location attribute of object
            if longitude and latitude:
                self.location = (longitude, latitude)

        self.save()

    def add_tags(self, tags):
        print(tags, "tags")
        self.tags = tags
        self.save()

    def add_location(self, loc):
        self.location = loc
        self.save()

    def add_date(self, date):
        self.date = date
        self.save()

    def remove_attr(self, attr):
        if attr == 'loc':
            self.location = None
        elif attr == 'date':
            self.date = None
        self.save()


def photo_tags_as_list(photos):
    for ph in photos:
        ph.tags = ph.tags.split(',')
    return photos


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
    shared_users = models.ManyToManyField(User, related_name='shared_collections')
    views = models.ManyToManyField(FilterView)
    cover = models.ImageField(default='empty_col.jpg')
    created_date = models.DateTimeField(default=timezone.now)
    photos = models.ManyToManyField(Photo, related_name='col_photos')

    def remove_photo_from_collection(self, photo):
        self.photos.remove(photo)
        self.save()

    def add_photo_to_collection(self, photo):
        self.photos.add(photo)
        self.save()

    def add_photos_to_collection(self, photos_ids):
        photos_to_be_added = []
        # photo objects are kept in dictionary to avoid cost of fetching from database in loop
        all_photos = {ph.id: ph for ph in Photo.objects.all()}
        for ph_id in photos_ids:
            photos_to_be_added.append(all_photos[int(ph_id)])
        self.photos.add(*photos_to_be_added)
        self.save()

    def remove_photos_from_collection(self, photos_ids):
        photos_to_be_removed = []
        # photo objects are kept in dictionary to avoid cost of fetching from database in loop
        all_photos = {ph.id: ph for ph in Photo.objects.all()}
        for ph_id in photos_ids:
            photos_to_be_removed.append(all_photos[int(ph_id)])
        self.photos.remove(*photos_to_be_removed)
        self.save()

    def unshare_with(self, user):
        self.shared_users.remove(user)
        self.save()

    def share_with(self, user):
        self.shared_users.add(user)
        self.save()
