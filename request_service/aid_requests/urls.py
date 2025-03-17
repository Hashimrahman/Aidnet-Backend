from django.urls import path
from . import views

urlpatterns = [
    path("test/", views.TestAPIView.as_view(), name="test-api"),
    path('create/',views.CreateRequestAPIView.as_view(), name='create-request')
]
