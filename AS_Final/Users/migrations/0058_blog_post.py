# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-30 08:58
from __future__ import unicode_literals

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0057_auto_20170929_1003'),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog_Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Title', models.CharField(max_length=200)),
                ('Content', ckeditor_uploader.fields.RichTextUploadingField()),
                ('Date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
