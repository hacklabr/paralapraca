# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20171226_1217'),
        ('paralapraca', '0005_auto_20171204_1006'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site_logo', models.ImageField(upload_to=core.utils.HashName(b'site_logo', b'type'), null=True, verbose_name='Site Logo', blank=True)),
                ('text', models.TextField(default=b'', verbose_name='Content')),
                ('type', models.CharField(max_length=127, verbose_name='Certificate Type', choices=[(b'receipt', 'Receipt'), (b'certificate', 'Certificate')])),
                ('certificate_template', models.ForeignKey(to='core.CertificateTemplate')),
                ('contract', models.ForeignKey(to='paralapraca.Contract')),
            ],
            options={
                'verbose_name': 'Certificate Data',
            },
        ),
        migrations.AlterUniqueTogether(
            name='certificatedata',
            unique_together=set([('contract', 'certificate_template', 'type')]),
        ),
    ]
