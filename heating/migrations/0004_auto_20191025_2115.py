# Generated by Django 2.2.6 on 2019-10-25 21:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heating', '0003_auto_20191025_2105'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sensor',
            options={'verbose_name': 'Sensor', 'verbose_name_plural': 'Sensors'},
        ),
        migrations.AlterModelOptions(
            name='sensordata',
            options={'verbose_name': 'SensorData', 'verbose_name_plural': 'SensorData'},
        ),
    ]
