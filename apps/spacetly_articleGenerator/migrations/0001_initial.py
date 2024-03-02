# Generated by Django 5.0.1 on 2024-02-14 20:14

import django.db.models.deletion
import django.utils.timezone
import mptt.fields
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=50)),
                ('num_results', models.IntegerField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=100)),
                ('language', models.CharField(max_length=50)),
                ('num_keywords', models.IntegerField(default=10)),
            ],
        ),
        migrations.CreateModel(
            name='Subheading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('tone_of_voice', models.CharField(max_length=100)),
                ('language', models.CharField(max_length=50)),
                ('num_keywords', models.IntegerField()),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('keywords', models.ManyToManyField(to='spacetly_articleGenerator.keyword')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='spacetly_articleGenerator.subheading')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_title', models.CharField(max_length=100)),
                ('tone_of_voice', models.CharField(max_length=100)),
                ('language', models.CharField(max_length=50)),
                ('slug', models.SlugField(help_text='Unique URL path to access this article. Generated automatically based on the title.', max_length=255, unique=True)),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for this article, generated automatically.', unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='Date and time when this article was created.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when this article was last updated.')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='spacetly_articleGenerator.image')),
                ('selected_keywords', models.ManyToManyField(to='spacetly_articleGenerator.keyword')),
                ('subheadings', models.ManyToManyField(to='spacetly_articleGenerator.subheading')),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=100)),
                ('num_titles', models.IntegerField()),
                ('tone_of_voice', models.CharField(max_length=100)),
                ('language', models.CharField(max_length=50)),
                ('keywords', models.ManyToManyField(to='spacetly_articleGenerator.keyword')),
            ],
        ),
        migrations.CreateModel(
            name='SavedArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_at', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spacetly_articleGenerator.article')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'article')},
            },
        ),
    ]
