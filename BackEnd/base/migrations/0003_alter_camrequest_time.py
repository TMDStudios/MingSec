# Generated by Django 3.2.18 on 2023-04-13 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20230412_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camrequest',
            name='time',
            field=models.FloatField(null=True),
        ),
    ]
