# Generated by Django 3.0.5 on 2020-05-11 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpg', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commodity_info',
            name='com_name',
            field=models.CharField(max_length=250),
        ),
    ]
