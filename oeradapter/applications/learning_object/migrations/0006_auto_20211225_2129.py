# Generated by Django 3.2.7 on 2021-12-26 02:29

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('learning_object', '0005_auto_20211225_0933'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestapi',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 25, 21, 29, 3, 901526, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='requestapi',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='learningobject',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 25, 21, 29, 3, 898740, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='learningobject',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 26, 21, 29, 3, 898740, tzinfo=utc)),
        ),
    ]
