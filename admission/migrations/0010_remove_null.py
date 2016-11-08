# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-08 09:49
from __future__ import unicode_literals
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0009_populate_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='form',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='option',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]