# Generated by Django 5.0.1 on 2024-02-20 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spacetly_templates', '0005_remove_usertemplate_num_of_results'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertemplate',
            name='num_of_results',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
