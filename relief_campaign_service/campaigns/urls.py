from django.urls import path

from . import views

urlpatterns = [
    # path('create/', views.CampaignCreateView.as_view(), name='create-campaign'),
    # path('get-campaigns/', views.CampaignListView.as_view(), name='get-campaigns'),
    path('get-create-campaigns/', views.CampaignView.as_view(), name='get-campaigns'),
    # path('<uuid:campaign_id>/join/', views.CampaignJoinView.as_view(), name='campaign-join'),
    # path('<uuid:campaign_id>/leave/', views.LeaveCampaignView.as_view(), name='leave-campaign'),
    path('<uuid:campaign_id>/participation/', views.CampaignParticipationView.as_view(), name='join-or-leave-campaign'),
    path('user/', views.UserDetailsAPIView.as_view(), name='fetch-user'),
    path('edit/<uuid:campaign_id>/', views.UpdateCampaignStatusAPIView.as_view(), name='update-camp-status'),
    path('user-campaigns/', views.UserCampaignsAPIView.as_view(), name='user-campaigns'),
]
