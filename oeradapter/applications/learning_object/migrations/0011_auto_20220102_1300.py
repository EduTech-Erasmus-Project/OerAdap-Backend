# Generated by Django 3.2.7 on 2022-01-02 18:00

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('learning_object', '0010_auto_20220102_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningobject',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='learningobject',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 3, 13, 0, 18, 734248)),
        ),
        migrations.AlterField(
            model_name='requestapi',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
