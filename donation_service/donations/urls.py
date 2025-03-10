from django.urls import path

from . import views

urlpatterns = [
    path('test/', views.TestAPI.as_view(), name='test-view'),
    path('donate/', views.DonationCreateAPIView.as_view(), name='donate'),
    path('all-donations/', views.AllDonationAPIView.as_view(), name='all-donations'),
    path('my-donations/', views.DonorDonationAPIView.as_view(), name='my-donations'),
    path('donation-details/', views.DonationDetailedAPIView.as_view(), name='donation-detailed-view'),
    path('<int:donation_id>/delete-donation/', views.DeleteDonationAPIView.as_view(), name='delete-donation'),
    path('<int:donation_id>/update/', views.UpdateDonationAPIView.as_view(), name='update-donation'),
]
