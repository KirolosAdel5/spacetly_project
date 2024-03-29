# Generated by Django 5.0.1 on 2024-03-18 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spacetly_templates', '0015_rename_output_data_usertemplate_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='template',
            name='favorite',
        ),
        migrations.AddField(
            model_name='template',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='favoritetemplate',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='favoritetemplate',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='usertemplate',
            name='content',
            field=models.TextField(blank=True),
        ),
    ]
