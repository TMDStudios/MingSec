# Generated by Django 3.2.18 on 2023-05-13 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20230422_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camrequest',
            name='time',
            field=models.BigIntegerField(default=1683941560414),
        ),
        migrations.AlterField(
            model_name='statusreport',
            name='status',
            field=models.CharField(max_length=255),
        ),
    ]