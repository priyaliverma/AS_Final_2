# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-10-01 09:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0059_remove_blog_post_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog_post',
            name='FriendlyDate',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
