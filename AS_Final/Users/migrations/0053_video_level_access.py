# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-24 23:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0052_workout_template_block_end'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='Level_Access',
            field=models.IntegerField(default=0),
        ),
    ]
