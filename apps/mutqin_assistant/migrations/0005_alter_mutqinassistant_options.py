# Generated by Django 5.0.1 on 2024-03-18 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mutqin_assistant', '0004_rename_qeuestion_mutqinassistant_question'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mutqinassistant',
            options={'ordering': ['-created_at']},
        ),
    ]
