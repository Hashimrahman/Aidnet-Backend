# views.py
from rest_framework import generics, status, views
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Campaign, ChatRoom
from .serializers import CampaignSerializer, ChatRoomSerializer


class CampaignListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        campaigns = Campaign.objects.all()
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatRoomListAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
        chat_rooms = ChatRoom.objects.all()
        serializer = ChatRoomSerializer(chat_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
