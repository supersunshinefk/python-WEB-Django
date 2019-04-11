# Generated by Django 2.0.4 on 2018-08-16 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('script', models.TextField(blank=True, max_length=2048, null=True, verbose_name='script')),
                ('version', models.CharField(blank=True, max_length=10, null=True, verbose_name='version')),
                ('remark', models.TextField(blank=True, max_length=2048, null=True, verbose_name='remark')),
                ('template', models.TextField(blank=True, max_length=2048, null=True, verbose_name='template')),
                ('is_available', models.BooleanField(default=1, verbose_name='is_available')),
                ('reference', models.CharField(blank=True, max_length=64, null=True, verbose_name='reference')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('data_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('filter_id', models.CharField(max_length=32, unique=True, verbose_name='filter_id')),
                ('filter_name', models.CharField(max_length=32, null=True, verbose_name='filter_name')),
            ],
            options={
                'verbose_name_plural': 'data_filter',
                'db_table': 'boss_data_filter',
                'ordering': ['-filter_id'],
                'verbose_name': 'data_filter',
            },
        ),
        migrations.CreateModel(
            name='DataOrganizer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('script', models.TextField(blank=True, max_length=2048, null=True, verbose_name='script')),
                ('version', models.CharField(blank=True, max_length=10, null=True, verbose_name='version')),
                ('remark', models.TextField(blank=True, max_length=2048, null=True, verbose_name='remark')),
                ('template', models.TextField(blank=True, max_length=2048, null=True, verbose_name='template')),
                ('is_available', models.BooleanField(default=1, verbose_name='is_available')),
                ('reference', models.CharField(blank=True, max_length=64, null=True, verbose_name='reference')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('data_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('organizer_id', models.CharField(max_length=32, unique=True, verbose_name='organizer_id')),
                ('organizer_name', models.CharField(max_length=32, null=True, verbose_name='organizer_name')),
            ],
            options={
                'verbose_name_plural': 'data_organizer',
                'db_table': 'boss_data_organizer',
                'ordering': ['-organizer_id'],
                'verbose_name': 'data_organizer',
            },
        ),
    ]