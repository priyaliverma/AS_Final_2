# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-18 19:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0033_auto_20170918_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subworkout',
            name='Exercise_Type',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]
