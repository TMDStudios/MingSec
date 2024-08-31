# Generated by Django 3.2.18 on 2023-04-15 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20230413_2231'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlarmReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('camera', models.CharField(max_length=64)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='camrequest',
            name='time',
            field=models.BigIntegerField(default=1681523605373),
        ),
    ]