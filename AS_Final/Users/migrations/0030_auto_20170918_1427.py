# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-18 14:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0029_exercise_description_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='workout',
            name='Alloy_Passed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='workout',
            name='Completed',
            field=models.BooleanField(default=False),
        ),
    ]