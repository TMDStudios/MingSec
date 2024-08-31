# Generated by Django 3.2.18 on 2023-04-14 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_camrequest_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='camrequest',
            name='camera',
            field=models.CharField(default='msi-default', max_length=64),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='camrequest',
            name='time',
            field=models.BigIntegerField(default=1681439425403),
        ),
    ]
