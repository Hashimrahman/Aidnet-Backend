# Generated by Django 4.1 on 2025-02-27 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0005_remove_campaignparticipation_user_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaignparticipation",
            name="user_id",
            field=models.IntegerField(null=True),
        ),
    ]
