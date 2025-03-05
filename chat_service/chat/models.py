from django.db import models


class Campaign(models.Model):
    campaign_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=55)
    location = models.CharField(max_length=55)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name
