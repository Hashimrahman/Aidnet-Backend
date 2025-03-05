# views.py
from rest_framework import generics
from .models import Campaign
from .serializers import CampaignSerializer

class CampaignListView(generics.ListAPIView):
    queryset = Campaign.objects.all()  # Fetch all campaigns
    serializer_class = CampaignSerializer  # Use the CampaignSerializer to serialize the data
