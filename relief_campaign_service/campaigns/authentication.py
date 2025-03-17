import json
import logging
import uuid
from types import SimpleNamespace

import jwt
import pika
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger("django")


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        logger.info(f"Received Auth Header: {auth_header}")

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("No valid token found.")
            return None

        token = auth_header.split(" ")[1]

        try:
            decoded_token = jwt.decode(
                token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=["HS256"]
            )
            logger.info(f"Decoded JWT: {decoded_token}")

            user_id = decoded_token.get("user_id")
            logger.info(f"UserId : {user_id}")
            user_data = self.get_user_from_rabbitmq(user_id)

            if not user_data:
                raise AuthenticationFailed("User not found")

            logger.info(f"User fetched from RabbitMQ: {user_data}")

            # Convert the dictionary to an object
            user_object = SimpleNamespace(
                id=user_data["id"],
                email=user_data["email"],
                role=user_data["role"],
                is_authenticated=True,
            )

            return (user_object, None)
        except jwt.ExpiredSignatureError:
            logger.error("JWT Token has expired.")
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            logger.error("Invalid JWT Token.")
            raise AuthenticationFailed("Invalid token")

    def get_user_from_rabbitmq(self, user_id):
        logger.info(f"Fetching user_id {user_id} from RabbitMQ")

        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
        channel = connection.channel()

        result = channel.queue_declare(queue="", exclusive=True)
        reply_queue = result.method.queue
        correlation_id = str(uuid.uuid4())

        channel.basic_publish(
            exchange="",
            routing_key=settings.RABBITMQ_USER_SERVICE_QUEUE,
            properties=pika.BasicProperties(
                reply_to=reply_queue,
                correlation_id=correlation_id,
            ),
            body=json.dumps({"user_id": user_id}),
        )

        logger.info(f"Waiting for response in {reply_queue}")

        for method_frame, properties, body in channel.consume(
            queue=reply_queue, inactivity_timeout=5
        ):
            if properties and properties.correlation_id == correlation_id:
                channel.basic_ack(method_frame.delivery_tag)
                user_data = json.loads(body)
                logger.info(f"Received user data from RabbitMQ: {user_data}")
                channel.cancel()
                return user_data

        logger.warning("No user data received from RabbitMQ")
        return AnonymousUser()
