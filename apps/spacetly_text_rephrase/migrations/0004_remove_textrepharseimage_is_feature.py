# Generated by Django 5.0.1 on 2024-02-14 23:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spacetly_text_rephrase', '0003_alter_text_original_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='textrepharseimage',
            name='is_feature',
        ),
    ]
