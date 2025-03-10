# urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('campaigns/', views.CampaignListAPIView.as_view(), name='campaign-list'),
    path('chatrooms/', views.ChatRoomListAPIView.as_view(), name='chat-rooms')
]
