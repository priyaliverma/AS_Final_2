# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-02 16:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0002_remove_exercise_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='Video',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='exercises', to='Users.Video'),
        ),
    ]