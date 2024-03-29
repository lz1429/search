# Generated by Django 3.0.5 on 2020-05-11 16:25

import adminpg.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='authority_info',
            fields=[
                ('authority', models.IntegerField(primary_key=True, serialize=False)),
                ('describe', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='commodity_info',
            fields=[
                ('com_id', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('com_name', models.CharField(max_length=100)),
                ('com_img', models.URLField(max_length=250, null=True)),
                ('com_shop', models.CharField(max_length=30, null=True)),
                ('com_evaluate', models.CharField(max_length=30, null=True)),
                ('com_source', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='recommend',
            fields=[
                ('recom_id', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('recom_title', models.CharField(max_length=250)),
                ('recom_img', models.CharField(max_length=250)),
                ('recom_price', models.CharField(max_length=50, null=True)),
                ('recom_desc', models.CharField(max_length=254)),
                ('recom_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='pricecompare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_price', models.CharField(max_length=15, null=True)),
                ('max_date', models.DateTimeField()),
                ('min_price', models.CharField(max_length=15, null=True)),
                ('min_date', models.DateTimeField()),
                ('price_com_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                   to='adminpg.commodity_info')),
            ],
        ),
        migrations.CreateModel(
            name='price_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('price', models.CharField(max_length=15, null=True)),
                ('com_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpg.commodity_info')),
            ],
        ),
        migrations.CreateModel(
            name='admin_info',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('pwd', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=16)),
                ('email', models.EmailField(default='example.@email.com', max_length=254)),
                ('avatar', models.ImageField(null=True, upload_to=adminpg.models.path_and_rename)),
                ('avatarname', models.CharField(max_length=64)),
                ('phone', models.CharField(max_length=11)),
                ('register_data', models.DateTimeField()),
                ('authority_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                   to='adminpg.authority_info')),
            ],
        ),
    ]
