# Generated by Django 5.0.1 on 2024-02-22 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='mobile_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
