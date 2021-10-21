# Generated by Django 3.2.7 on 2021-10-20 14:58

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('learning_object', '0008_auto_20211016_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagelearningobject',
            name='preview_path',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='pagelearningobject',
            name='title',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='learningobject',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 21, 9, 58, 31, 817347)),
        ),
        migrations.AlterField(
            model_name='tagpagelearningobject',
            name='page_learning_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning_object.pagelearningobject'),
        ),
        migrations.AlterModelTable(
            name='pagelearningobject',
            table='page_learning_object',
        ),
        migrations.AlterModelTable(
            name='tagpagelearningobject',
            table='tag_page_learning_object',
        ),
        migrations.CreateModel(
            name='TagAdapted',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20)),
                ('text', models.TextField(blank=True, null=True)),
                ('html_text', models.TextField(blank=True, null=True)),
                ('path_src', models.TextField(blank=True, null=True)),
                ('path_preview', models.URLField(null=True)),
                ('tag_page_learning_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning_object.tagpagelearningobject')),
            ],
            options={
                'db_table': 'tag_adapted',
            },
        ),
    ]