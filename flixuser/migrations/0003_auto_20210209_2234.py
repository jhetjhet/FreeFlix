# Generated by Django 3.1.5 on 2021-02-09 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flixuser', '0002_auto_20210209_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flixer',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
