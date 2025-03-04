import uuid
from django.db import models
from django.core.exceptions import ValidationError


class Campaign(models.Model):

    class UrgencyLevel(models.TextChoices):
        HIGH = "High", "High"
        MEDIUM = "Medium", "Medium"
        LOW = "Low", "Low"

    class Status(models.TextChoices):
        ONGOING = "ongoing", "Ongoing"
        ENDED = "ended", "Ended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField(auto_now_add=True, null=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.ONGOING)
    organizer = models.IntegerField(default=1)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_capacity = models.PositiveIntegerField(default=0)
    remaining_capacity = models.PositiveIntegerField(default=0)
    volunteers_required = models.PositiveIntegerField(default=0)
    volunteers_registered = models.PositiveIntegerField(default=0)
    urgency = models.CharField(
        max_length=10, choices=UrgencyLevel.choices, default=UrgencyLevel.MEDIUM
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_capacity = self.max_capacity
        super().save(*args, **kwargs)

    def join_campaign(self, user_id, participant_type):
        if self.participations.filter(user_id=user_id).exists():
            raise ValidationError("User has already joined this campaign.")

        if self.remaining_capacity <= 0:
            raise ValidationError("No remaining capacity in the campaign.")

        if participant_type == CampaignParticipation.VOLUNTEER:
            if self.volunteers_registered >= self.volunteers_required:
                raise ValidationError("No volunteer slots available.")
            self.volunteers_registered += 1

        self.remaining_capacity -= 1
        self.save()

        return CampaignParticipation.objects.create(
            campaign=self, user_id=user_id, participant_type=participant_type
        )

    def __str__(self):
        return self.name


class CampaignParticipation(models.Model):
    VOLUNTEER = "volunteer"
    AFFECTED = "affected"

    PARTICIPANT_TYPE_CHOICES = (
        (VOLUNTEER, "Volunteer"),
        (AFFECTED, "Affected"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="participations"
    )
    user_id = models.IntegerField(null=True)
    participant_type = models.CharField(
        max_length=20, choices=PARTICIPANT_TYPE_CHOICES, default=AFFECTED
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} joined {self.campaign.name} as {self.participant_type}"
