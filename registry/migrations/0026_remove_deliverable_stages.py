# Generated by Django 5.1.2 on 2024-11-21 14:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0025_deliverable_stages_project_number_of_deliverables'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliverable',
            name='stages',
        ),
    ]
