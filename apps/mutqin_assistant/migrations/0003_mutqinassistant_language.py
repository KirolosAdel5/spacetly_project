# Generated by Django 5.0.1 on 2024-03-13 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mutqin_assistant', '0002_alter_mutqinassistant_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='mutqinassistant',
            name='language',
            field=models.CharField(default='en', max_length=100),
        ),
    ]
