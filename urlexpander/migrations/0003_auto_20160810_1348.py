# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-10 20:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urlexpander', '0002_auto_20160810_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='url',
            name='wayback_date',
            field=models.CharField(max_length=30, null=True),
        ),
    ]