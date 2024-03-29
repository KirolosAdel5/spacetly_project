# Generated by Django 5.0.1 on 2024-02-18 14:39

import django.db.models.deletion
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
            name='TemplateSpecification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='TemplateType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Required and unique', max_length=255, unique=True, verbose_name='Category Name')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='Category safe URL')),
                ('is_active', models.BooleanField(default=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='spacetly_templates.category')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='template_icons')),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
                ('category', mptt.fields.TreeForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spacetly_templates.category')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('template_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spacetly_templates.templatetype')),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spacetly_templates.template')),
            ],
        ),
        migrations.CreateModel(
            name='TemplateSpecificationField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=255)),
                ('is_required', models.BooleanField(default=False)),
                ('field_type', models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('file', 'File')], default='text', max_length=20)),
                ('specification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='spacetly_templates.templatespecification')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specification_values', to='spacetly_templates.template')),
            ],
        ),
        migrations.AddField(
            model_name='templatespecification',
            name='template_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spacetly_templates.templatetype'),
        ),
    ]
