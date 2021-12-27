# Generated by Django 3.2.7 on 2021-12-26 19:04

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('learning_object', '0006_auto_20211225_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningobject',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 26, 14, 4, 47, 293027, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='learningobject',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 27, 14, 4, 47, 293027, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='requestapi',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 26, 14, 4, 47, 297952, tzinfo=utc)),
        ),
    ]
