# Generated by Django 3.2.7 on 2021-10-16 02:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_object', '0003_auto_20211015_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningobject',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 16, 21, 48, 48, 351004)),
        ),
    ]