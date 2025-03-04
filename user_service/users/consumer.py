# import pika
# import json
# import django
# import os
# import sys

# # Add project root directory to Python path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_service.settings")
# django.setup()

# from django.contrib.auth import get_user_model

# User = get_user_model()

# RABBITMQ_HOST = "rabbitmq"
# RABBITMQ_USER = "user"
# RABBITMQ_PASS = "password"
# QUEUE_NAME = "user_service_queue"

# def get_user_details(user_id):
#     """Fetch user details from the database."""
#     try:
#         user = User.objects.get(id=user_id)
#         return {
#             "id": user.id,
#             "email": user.email,
#             "role": user.role,
#             "is_authenticated": True,
#         }
#     except User.DoesNotExist:
#         return {"error": "User not found"}

# def callback(ch, method, properties, body):
#     """Handles incoming messages from other services."""
#     print("✅ Received message:", body)

#     request_data = json.loads(body)
#     user_id = request_data.get("user_id")

#     response_data = get_user_details(user_id)
#     print("🔄 Processed user data:", response_data)

#     # Ensure reply_to is set before publishing a response
#     if properties.reply_to:
#         ch.basic_publish(
#             exchange="",
#             routing_key=str(properties.reply_to),  # Ensure routing key is string
#             body=json.dumps(response_data),
#             properties=pika.BasicProperties(
#                 correlation_id=properties.correlation_id
#             ),
#         )
#         print(f"📩 Sent response to {properties.reply_to}")

#     ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message
#     print("✅ Message acknowledged")

# def start_consumer():
#     """Connect to RabbitMQ and start listening for messages."""
#     credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
#     channel = connection.channel()

#     channel.queue_declare(queue=QUEUE_NAME, durable=True)
#     channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

#     print(" [*] Waiting for authentication requests...")
#     try:
#         channel.start_consuming()
#     except KeyboardInterrupt:
#         print("\n🛑 Stopping consumer...")
#         channel.stop_consuming()
#         connection.close()
#         print("✅ Connection closed.")

# if __name__ == "__main__":
#     start_consumer()



import pika
import json
import os
import django
import sys

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "User_Service.settings")

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

django.setup()

from users.models import CustomUser

def process_message(ch, method, properties, body):
    user_request = json.loads(body)
    user_id = user_request.get("user_id")

    print(f"Processing request for user {user_id}")

    try:
        user = CustomUser.objects.get(id=user_id)
        
        user_data = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
    except CustomUser.DoesNotExist:
        user_data = {"error": "User not found"}

    response = json.dumps(user_data)

    if properties.reply_to:
        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=response,
        )
        print(f"Sent response to {properties.reply_to}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="rabbitmq",
        credentials=pika.PlainCredentials("user", "password")
    )
)
channel = connection.channel()
channel.queue_declare(queue="user_service_queue", durable=True)

channel.basic_consume(queue="user_service_queue", on_message_callback=process_message)

print("✅ Waiting for messages...")
channel.start_consuming()
