# import json
# import pika
# from .models import Campaign


# def consume_campaign_events():
#     """Listen for campaign creation events and store them in the database."""
#     connection = pika.BlockingConnection(
#             pika.ConnectionParameters(
#                 host="rabbitmq", credentials=pika.PlainCredentials("user", "password")
#             )
#         )
#     channel = connection.channel()
#     channel.queue_declare(queue="campaign_created")

#     def callback(ch, method, properties, body):
#         event = json.loads(body)
#         print(f"Received campaign event: {event}")

#         # Save campaign data locally
#         Campaign.objects.update_or_create(
#             campaign_id=event["campaign_id"],
#             defaults={
#                 "name": event["name"],
#                 "description": event["description"],
#                 "start_date": event["start_date"],
#                 "end_date": event["end_date"],
#                 "location": event["location"],
#                 "status": event["status"],
#             },
#         )

#     channel.basic_consume(
#         queue="campaign_created", on_message_callback=callback, auto_ack=True
#     )
#     print("Waiting for campaign events...")
#     channel.start_consuming()

import json
import pika
import logging
from .models import Campaign

# Set up logging
# logging.basicConfig(
#     level=logging.INFO,  # You can change this to DEBUG, ERROR, etc.
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )
logger = logging.getLogger('django')

def consume_campaign_events():
    """Listen for campaign creation events and store them in the database."""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq", credentials=pika.PlainCredentials("user", "password")
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue="campaign_created")

    def callback(ch, method, properties, body):
        try:
            event = json.loads(body)
            # Log each field individually
            logger.info(f"Received campaign event - campaign_id: {event['campaign_id']}")
            logger.info(f"Received campaign event - name: {event['name']}")
            logger.info(f"Received campaign event - description: {event['description']}")
            logger.info(f"Received campaign event - start_date: {event['start_date']}")
            logger.info(f"Received campaign event - end_date: {event['end_date']}")
            logger.info(f"Received campaign event - location: {event['location']}")
            logger.info(f"Received campaign event - status: {event['status']}")

            # Save campaign data locally
            Campaign.objects.update_or_create(
                campaign_id=event["campaign_id"],
                defaults={
                    "name": event["name"],
                    "description": event["description"],
                    "start_date": event["start_date"],
                    "end_date": event["end_date"],
                    "location": event["location"],
                    "status": event["status"],
                },
            )

        except Exception as e:
            logger.error(f"Error processing campaign event: {e}")

    channel.basic_consume(
        queue="campaign_created", on_message_callback=callback, auto_ack=True
    )
    logger.info("Waiting for campaign events...")
    channel.start_consuming()
