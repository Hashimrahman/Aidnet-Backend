# Generated by Django 4.1 on 2025-02-27 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "campaigns",
            "0002_rename_max_volunteers_campaign_volunteers_required_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="campaign",
            name="end_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="campaign",
            name="status",
            field=models.CharField(
                choices=[("ongoing", "Ongoing"), ("ended", "Ended")],
                default="ongoing",
                max_length=50,
            ),
        ),
    ]
