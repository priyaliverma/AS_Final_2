# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-24 07:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0037_auto_20170923_0926'),
    ]

    operations = [
        migrations.AddField(
            model_name='subworkout',
            name='Strength_Drop',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='subworkout',
            name='Strength_Stop',
            field=models.IntegerField(default=0),
        ),
    ]
