# Generated by Django 4.0.1 on 2022-01-20 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared_photo_library', '0018_filterview_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filterview',
            name='end_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='filterview',
            name='start_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='date',
            field=models.DateTimeField(null=True),
        ),
    ]
