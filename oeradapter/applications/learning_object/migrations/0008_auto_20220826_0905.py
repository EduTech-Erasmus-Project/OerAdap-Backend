# Generated by Django 3.2.7 on 2022-08-26 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_object', '0007_auto_20220811_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadatainfo',
            name='id_learning',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metadatainfo',
            name='audio_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metadatainfo',
            name='img_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metadatainfo',
            name='text_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metadatainfo',
            name='video_number',
            field=models.IntegerField(default=0),
        ),
    ]
