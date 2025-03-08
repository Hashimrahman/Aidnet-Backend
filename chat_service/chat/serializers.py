# serializers.py
from rest_framework import serializers
from .models import Campaign, ChatRoom

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'  # This will include all fields of the model

class ChatRoomSerializer(serializers.ModelSerializer):
    campaignId = serializers.UUIDField(source='campaign.campaign_id')
    name = serializers.CharField()
    
    class Meta:
        model = ChatRoom
        fields = ['id','name','campaignId']
