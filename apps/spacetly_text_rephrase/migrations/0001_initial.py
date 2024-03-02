# Generated by Django 5.0.1 on 2024-02-14 20:14

import django.db.models.deletion
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
            name='Text',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_text', models.TextField()),
                ('rephrased_text', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for this text repharse, generated automatically.', unique=True)),
                ('font_size', models.IntegerField(default=12)),
                ('font_color', models.CharField(default='#001a78', max_length=50)),
                ('text_alignment', models.CharField(default='right', max_length=20)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TextRepharseImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Upload an image related to the rephrased text', upload_to='images/text_rephrased_images/', verbose_name='image')),
                ('alt_text', models.CharField(blank=True, help_text='Please add alternative text', max_length=255, null=True, verbose_name='Alternative text')),
                ('is_feature', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('text', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rephrased_images', to='spacetly_text_rephrase.text')),
            ],
            options={
                'verbose_name': 'Text Rephrase Image',
                'verbose_name_plural': 'Text Rephrase Images',
            },
        ),
    ]
