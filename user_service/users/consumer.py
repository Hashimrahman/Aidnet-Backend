import json
import os
import sys

import django
import pika

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
