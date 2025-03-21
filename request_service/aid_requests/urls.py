from django.urls import path
from . import views

urlpatterns = [
    path("test/", views.TestAPIView.as_view(), name="test-api"),
    path('create-get/',views.RequestAPIView.as_view(), name='create-get-request'),
    path('<int:pk>/cancel/',views.CancelRequestAPIView.as_view(), name='cancel-request')
]
