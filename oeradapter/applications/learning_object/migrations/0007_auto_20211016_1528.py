# Generated by Django 3.2.7 on 2021-10-16 20:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_object', '0006_auto_20211016_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataatribute',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='learningobject',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 17, 15, 28, 17, 760066)),
        ),
        migrations.AlterField(
            model_name='tagpagelearningobject',
            name='html_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tagpagelearningobject',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
