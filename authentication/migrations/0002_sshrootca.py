# Generated by Django 5.0.4 on 2024-06-14 13:24

import datetime
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SSHRootCA',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30, unique=True)),
                ('public_key', models.TextField()),
                ('private_key', models.TextField()),
                ('last_serial', models.PositiveIntegerField(default=0, editable=False)),
                ('validity', models.DurationField(default=datetime.timedelta(seconds=14400))),
                ('principal', models.CharField(default='iotinga', max_length=30)),
            ],
            options={
                'verbose_name_plural': 'SSH Root CA',
            },
        ),
    ]
