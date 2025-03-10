import requests
from django.conf import settings
from rest_framework.permissions import BasePermission

USER_SERVICE_URL = "http://localhost:8000/user/users/" 

class IsAdminFromToken(BasePermission):
    def has_permission(self, request, view):
        user_id = request.user.id
        if not user_id:
            return False

        response = requests.get(f"{USER_SERVICE_URL}{user_id}/")

        if response.status_code == 200:
            user_data = response.json()
            return user_data.get("role") == "admin"

        return False
