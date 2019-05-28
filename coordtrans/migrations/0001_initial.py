# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlPoint',
            fields=[
                ('pid', models.CharField(max_length=8, verbose_name='Point ID.', primary_key=True, serialize=False)),
                ('geog_x', models.DecimalField(decimal_places=3, verbose_name='Geographic - E', max_digits=12)),
                ('geog_y', models.DecimalField(decimal_places=3, verbose_name='Geographic - N', max_digits=12)),
                ('cass_x', models.DecimalField(decimal_places=3, verbose_name='Cassini - E', max_digits=12)),
                ('cass_y', models.DecimalField(decimal_places=3, verbose_name='Cassini - N', max_digits=12)),
                ('utm_x', models.DecimalField(decimal_places=3, verbose_name='U.T.M. - E', max_digits=12)),
                ('utm_y', models.DecimalField(decimal_places=3, verbose_name='U.T.M. - N', max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='SheetReference',
            fields=[
                ('shtno', models.CharField(max_length=8, verbose_name='Sheet No.', primary_key=True, serialize=False)),
                ('scan', models.ImageField(upload_to='sheets/', verbose_name='Sheet Image')),
                ('pt1', models.ForeignKey(to='coordtrans.ControlPoint', related_name='control_pt1', verbose_name='Point 1')),
                ('pt2', models.ForeignKey(to='coordtrans.ControlPoint', related_name='control_pt2', verbose_name='Point 2')),
                ('pt3', models.ForeignKey(to='coordtrans.ControlPoint', related_name='control_pt3', verbose_name='Point 3')),
                ('pt4', models.ForeignKey(to='coordtrans.ControlPoint', related_name='control_pt4', verbose_name='Point 4')),
            ],
            options={
                'ordering': ['shtno'],
            },
        ),
        migrations.CreateModel(
            name='TransRequest',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('inpoints', models.IntegerField(verbose_name='Points Given', default=-1)),
                ('points', models.IntegerField(verbose_name='Points Transformed')),
                ('trtype', models.CharField(choices=[('cassini', 'Cassini'), ('utm', 'U.T.M.')], max_length=8, verbose_name='Transformation Type')),
                ('datedone', models.DateField(verbose_name='Date Done', default=django.utils.timezone.now)),
                ('sheet', models.ForeignKey(to='coordtrans.SheetReference')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Transformation Request',
            },
        ),
    ]
