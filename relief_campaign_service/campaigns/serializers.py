from rest_framework import serializers

from .models import Campaign, CampaignParticipation


class CampaignParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignParticipation
        fields = ("id", "user_id", "participant_type", "joined_at")


class CampaignSerializer(serializers.ModelSerializer):
    participations = CampaignParticipationSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = (
            "id",
            "name",
            "description",
            "location",
            "start_date",
            "status",
            "organizer",
            "collected_amount",
            "max_capacity",
            "remaining_capacity",
            "volunteers_required",
            "volunteers_registered",
            "participations",
            "urgency",
        )
        read_only_fields = ("remaining_capacity", "volunteers_registered")
