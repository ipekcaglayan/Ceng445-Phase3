# Generated by Django 4.0.1 on 2022-01-15 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared_photo_library', '0003_filterview_remove_view_owner_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='photo',
            field=models.FileField(blank=True, upload_to=''),
        ),
    ]
