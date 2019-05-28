# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('authtools', '0003_auto_20160128_0912'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, primary_key=True, serialize=False)),
                ('slug', models.UUIDField(blank=True, editable=False, default=uuid.uuid4)),
                ('picture', models.ImageField(upload_to='profile_pics/%Y-%m-%d/', blank=True, verbose_name='Profile picture', null=True)),
                ('bio', models.CharField(max_length=200, blank=True, verbose_name='Short Bio', null=True)),
                ('email_verified', models.BooleanField(verbose_name='Email verified', default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
