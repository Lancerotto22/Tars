# Generated by Django 5.0.4 on 2024-06-17 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0013_remove_project_certificate_project_ca_certificate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='lang',
            field=models.CharField(default='italian', help_text='mother tongue of the customer', max_length=30),
        ),
    ]
