# Generated by Django 4.0.1 on 2022-01-16 13:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shared_photo_library', '0014_remove_collection_views_filterview_collection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filterview',
            name='shared_users',
            field=models.ManyToManyField(related_name='shared_views', to=settings.AUTH_USER_MODEL),
        ),
    ]