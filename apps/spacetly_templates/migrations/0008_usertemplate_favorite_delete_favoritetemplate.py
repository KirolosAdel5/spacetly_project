# Generated by Django 5.0.1 on 2024-03-14 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spacetly_templates', '0007_alter_usertemplate_num_of_results'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertemplate',
            name='favorite',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='FavoriteTemplate',
        ),
    ]
