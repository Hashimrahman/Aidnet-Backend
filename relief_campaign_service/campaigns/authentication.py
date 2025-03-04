# import requests
# import logging
# from types import SimpleNamespace
# from django.conf import settings
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework_simplejwt.authentication import JWTAuthentication

# logger = logging.getLogger('django')

# class CustomJWTAuthentication(JWTAuthentication):
#     def get_user(self, validated_token):
#         user_id = validated_token.get("user_id")

#         if not user_id:
#             raise AuthenticationFailed("Invalid token")

#         user_service_url = f"{settings.USER_SERVICE_URL}user-details/{user_id}"
        
#         logger.info(f"Requesting user data from: {user_service_url}")

#         try:
#             response = requests.get(user_service_url, headers={"Authorization": f"Bearer {validated_token}"})
#             if response.status_code == 200:
#                 user_data = response.json()
#                 dummy_user = SimpleNamespace(**user_data, is_authenticated=True)
#                 return dummy_user

#             else:
#                 raise AuthenticationFailed("User not found")
#         except requests.exceptions.RequestException:
#             logger.error(f"Error while contacting user service at: {user_service_url}")
#             raise AuthenticationFailed("User service unavailable")


# import pika
# import json
# import uuid
# import logging
# from types import SimpleNamespace
# from django.conf import settings
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework_simplejwt.authentication import JWTAuthentication

# logger = logging.getLogger('django')

# class CustomJWTAuthentication(JWTAuthentication):
#     def get_user(self, validated_token):
#         user_id = validated_token.get("user_id")
#         if not user_id:
#             raise AuthenticationFailed("Invalid Token")
        
#         logger.info(f"Requesting user data for user_id: {user_id}")
        
#         correlation_id = str(uuid.uuid4())
#         response_queue = f"response_queue_{correlation_id}"
        
#         try:
#             connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
#             channel = connection.channel()
            
#             # Declare a temporary queue for response
#             channel.queue_declare(queue=response_queue, exclusive=True)
            
#             request_data = json.dumps({"user_id": user_id})
#             channel.basic_publish(
#                 exchange="",
#                 routing_key="user_service_queue",
#                 properties=pika.BasicProperties(
#                     reply_to=response_queue,
#                     correlation_id=correlation_id
#                 ),
#                 body=request_data
#             )
            
#             user_response = None  # Initialize response variable

#             # Callback function to handle the response
#             def callback(ch, method, properties, body):
#                 nonlocal user_response  # Use nonlocal instead of global
#                 if properties.correlation_id == correlation_id:
#                     user_response = json.loads(body)
#                     ch.stop_consuming()

#             # Consume the response
#             channel.basic_consume(queue=response_queue, on_message_callback=callback, auto_ack=True)
            
            # logger.info(f"Waiting for user service response for user_id: {user_id}")
#             channel.start_consuming()
            
#             connection.close()  # Close after consuming
            
#             # Process user response
#             if user_response and user_response.get("status") == "Success":
#                 user_data = user_response["data"]
#                 dummy_user = SimpleNamespace(**user_data, is_authenticated=True)
#                 return dummy_user
#             else:
#                 raise AuthenticationFailed("User not found")
        
#         except Exception as e:
#             logger.error(f"Error while contacting user service: {str(e)}")
#             raise AuthenticationFailed("User Service unavailable")


import jwt
import pika
import json
import logging
import uuid
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from types import SimpleNamespace

logger = logging.getLogger('django')

class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        logger.info(f"Received Auth Header: {auth_header}")  # Debugging

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("No valid token found.")
            return None

        token = auth_header.split(" ")[1]

        try:
            decoded_token = jwt.decode(token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=["HS256"])
            logger.info(f"Decoded JWT: {decoded_token}")  # Debugging

            user_id = decoded_token.get("user_id")
            logger.info(f"UserId : {user_id}")  # Debugging
            user_data = self.get_user_from_rabbitmq(user_id)

            if not user_data:
                raise AuthenticationFailed("User not found")

            logger.info(f"User fetched from RabbitMQ: {user_data}")  # Debugging

            # ✅ Convert the dictionary to an object that mimics Django User
            user_object = SimpleNamespace(
                id=user_data["id"],
                email=user_data["email"],
                role=user_data["role"],
                is_authenticated=True,  # ✅ DRF requires this attribute
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

        # Declare an exclusive queue for replies
        result = channel.queue_declare(queue="", exclusive=True)
        reply_queue = result.method.queue
        correlation_id = str(uuid.uuid4())  # Generate unique correlation ID

        # Send request with reply_to and correlation_id
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

        # Wait for the response
        for method_frame, properties, body in channel.consume(queue=reply_queue, inactivity_timeout=5):
            if properties and properties.correlation_id == correlation_id:
                channel.basic_ack(method_frame.delivery_tag)
                user_data = json.loads(body)
                logger.info(f"Received user data from RabbitMQ: {user_data}")
                channel.cancel()
                return user_data

        logger.warning("No user data received from RabbitMQ")
        return AnonymousUser()


