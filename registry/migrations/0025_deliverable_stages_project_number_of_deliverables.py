# Generated by Django 5.1.2 on 2024-11-21 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0024_deliverable_stage_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverable',
            name='stages',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='number_of_deliverables',
            field=models.IntegerField(null=True),
        ),
    ]
