# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-11 13:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0004_auto_20170911_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='workout_template',
            name='Block',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='workout_template',
            name='Block_Num',
            field=models.IntegerField(default=0),
        ),
    ]