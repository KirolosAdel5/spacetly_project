# Generated by Django 5.0.1 on 2024-03-12 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spacetly_articleGenerator', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='articles',
            options={'ordering': ['-updated_at'], 'verbose_name': 'Article', 'verbose_name_plural': 'Articles'},
        ),
        migrations.AddField(
            model_name='articles',
            name='content',
            field=models.TextField(blank=True, help_text='Article content'),
        ),
    ]