# views.py
from rest_framework import generics, views, status
from rest_framework.response import Response
from .models import Campaign, ChatRoom
from .serializers import CampaignSerializer, ChatRoomSerializer

class CampaignListView(generics.ListAPIView):
    queryset = Campaign.objects.all()  # Fetch all campaigns
    serializer_class = CampaignSerializer  # Use the CampaignSerializer to serialize the data

class ChatRoomListAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
        chat_rooms = ChatRoom.objects.all()
        serializer = ChatRoomSerializer(chat_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

