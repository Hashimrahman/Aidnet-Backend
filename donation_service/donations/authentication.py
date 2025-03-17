import logging
from types import SimpleNamespace

import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger("django")


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")

        if not user_id:
            raise AuthenticationFailed("Invalid token")

        user_service_url = f"{settings.USER_SERVICE_URL}user-details/{user_id}"

        logger.info(f"Requesting user data from: {user_service_url}")

        try:
            response = requests.get(
                user_service_url, headers={"Authorization": f"Bearer {validated_token}"}
            )
            if response.status_code == 200:
                user_data = response.json()
                dummy_user = SimpleNamespace(**user_data, is_authenticated=True)
                return dummy_user

            else:
                raise AuthenticationFailed("User not found")
        except requests.exceptions.RequestException:
            logger.error(f"Error while contacting user service at: {user_service_url}")
            raise AuthenticationFailed("User service unavailable")
