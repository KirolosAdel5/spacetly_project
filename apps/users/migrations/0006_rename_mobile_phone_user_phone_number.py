# Generated by Django 5.0.1 on 2024-02-22 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_mobile_phone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='mobile_phone',
            new_name='phone_number',
        ),
    ]