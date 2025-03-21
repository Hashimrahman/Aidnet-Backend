# Generated by Django 4.1 on 2025-03-18 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aid_requests', '0002_request_is_cancelled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('resolved', 'Resolved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', max_length=15),
        ),
    ]
