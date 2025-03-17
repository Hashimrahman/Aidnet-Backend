from django.urls import path

# from .views import RegistrationView
from . import views

urlpatterns = [
    path("register/", views.RegistrationView.as_view(), name="register"),
    path(
        "verify-email/<uuid:token>/",
        views.VerifyEmailView.as_view(),
        name="verify-email",
    ),
    path("login/", views.LoginView.as_view(), name="login"),
    path("user-list/", views.ListUsersAPIView.as_view(), name="user-list"),
    path(
        "delete-user/<int:user_id>",
        views.DeleteUserAPIView.as_view(),
        name="delete-list",
    ),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path("user-details/<int:id>/", views.UserDetailView.as_view(), name="user-detail"),
    path("verify-token/", views.VerifyTokenView.as_view(), name="verify-token"),
]
