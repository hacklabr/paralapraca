# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paralapraca', '0006_auto_20171226_1217'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='description',
            field=models.TextField(help_text='Enter the contract description (optional)', verbose_name='description', blank=True),
        ),
    ]
