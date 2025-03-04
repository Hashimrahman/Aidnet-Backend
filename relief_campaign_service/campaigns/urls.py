from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CampaignCreateView.as_view(), name='create-campaign'),
    path('get-campaigns/', views.CampaignListView.as_view(), name='get-campaigns'),
    path('<uuid:campaign_id>/join/', views.CampaignJoinView.as_view(), name='campaign-join'),
    path('user/', views.UserDetailsAPIView.as_view(), name='fetch-user'),
    path('<uuid:campaign_id>/leave/', views.LeaveCampaignView.as_view(), name='leave-campaign'),
    path('edit/<uuid:campaign_id>/', views.UpdateCampaignStatuAPIView.as_view(), name='update-camp-status'),
    path('user-campaigns/', views.UserCampaignsAPIView.as_view(), name='user-campaigns'),
]
