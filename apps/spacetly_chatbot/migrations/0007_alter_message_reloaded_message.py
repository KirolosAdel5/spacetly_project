# Generated by Django 5.0.1 on 2024-03-12 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spacetly_chatbot', '0006_message_reloaded_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='reloaded_message',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
