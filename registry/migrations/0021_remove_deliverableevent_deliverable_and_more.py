# Generated by Django 5.1.2 on 2024-11-12 09:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0020_deliverable_delivery_download_uri_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliverableevent',
            name='deliverable',
        ),
        migrations.DeleteModel(
            name='DeliverableConfiguration',
        ),
        migrations.DeleteModel(
            name='DeliverableEvent',
        ),
    ]
