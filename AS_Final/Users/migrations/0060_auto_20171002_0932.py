# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-02 09:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0059_auto_20171001_1401'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Blog_Post',
        ),
        migrations.AddField(
            model_name='exercise',
            name='Pause',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AddField(
            model_name='exercise',
            name='Tempo_Value',
            field=models.CharField(default='', max_length=10),
        ),
    ]
