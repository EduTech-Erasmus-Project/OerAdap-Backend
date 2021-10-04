# Generated by Django 3.2.7 on 2021-10-04 02:05

import applications.learning_object.models
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_object', '0005_alter_learningobject_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningobject',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 4, 21, 5, 51, 353643)),
        ),
        migrations.AlterField(
            model_name='learningobject',
            name='file_adapted',
            field=models.FileField(blank=True, null=True, upload_to=applications.learning_object.models.directory_path),
        ),
    ]
