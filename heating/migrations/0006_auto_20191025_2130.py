# Generated by Django 2.2.6 on 2019-10-25 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heating', '0005_auto_20191025_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor',
            name='address',
            field=models.CharField(blank=True, default='', max_length=128),
            preserve_default=False,
        ),
    ]
