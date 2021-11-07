import datetime
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LearningObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, null=True)),
                ('path_origin', models.TextField()),
                ('path_adapted', models.TextField()),
                ('user_ref', models.CharField(max_length=100)),
                ('file_folder', models.TextField()),
                ('preview_origin', models.URLField(null=True)),
                ('preview_adapted', models.URLField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(default=datetime.datetime(2021, 10, 30, 13, 14, 22, 889906))),
                ('file_adapted', models.URLField(null=True)),
            ],
            options={
                'db_table': 'learning_objects',
            },
        ),
        migrations.CreateModel(
            name='PageLearningObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.TextField()),
                ('title', models.CharField(max_length=200, null=True)),
                ('preview_path', models.URLField(null=True)),
                ('learning_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning_object.learningobject')),
            ],
            options={
                'db_table': 'page_learning_object',
            },
        ),
        migrations.CreateModel(
            name='TagPageLearningObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=20)),
                ('text', models.TextField(blank=True, null=True)),
                ('html_text', models.TextField(blank=True, null=True)),
                ('id_class_ref', models.CharField(max_length=20)),
                ('page_learning_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='learning_object.pagelearningobject')),
            ],
            options={
                'db_table': 'tag_page_learning_object',
            },
        ),
        migrations.CreateModel(
            name='TagAdapted',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20)),
                ('text', models.TextField(blank=True, null=True)),
                ('html_text', models.TextField(blank=True, null=True)),
                ('id_ref', models.CharField(max_length=20, null=True)),
                ('path_src', models.TextField(blank=True, null=True)),
                ('path_preview', models.URLField(max_length=255, null=True)),
                ('tag_page_learning_object', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='learning_object.tagpagelearningobject')),
            ],
            options={
                'db_table': 'tag_adapted',
            },
        ),
        migrations.CreateModel(
            name='DataAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atribute', models.CharField(max_length=100)),
                ('data_atribute', models.TextField()),
                ('type', models.CharField(blank=True, max_length=50, null=True)),
                ('tag_page_learning_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='atributes', to='learning_object.tagpagelearningobject')),
            ],
            options={
                'db_table': 'data_atribute',
            },
        ),
        migrations.CreateModel(
            name='AdaptationLearningObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(max_length=10)),
                ('areas', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=10), size=6)),
                ('learning_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning_object.learningobject')),
            ],
            options={
                'db_table': 'adaptations_learning_objects',
            },
        ),
    ]
