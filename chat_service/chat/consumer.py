import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_service.settings")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

import json
import logging
import time

import pika
from chat.models import Campaign, ChatRoom
from django.utils import timezone

logger = logging.getLogger("django")


def connect_to_rabbitmq():
    # connection to RabbitMQ
    max_retries = 5
    retry_delay = 5
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host="rabbitmq",
                    credentials=pika.PlainCredentials("user", "password"),
                )
            )
            logger.info("Successfully connected to RabbitMQ")
            return connection
        except Exception as e:
            logger.error(
                f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}"
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise Exception("Could not connect to RabbitMQ after multiple attempts")


def consume_campaign_events():
    # Listen for campaign creation events and store them in the db.
    try:
        connection = connect_to_rabbitmq()
        channel = connection.channel()
        channel.queue_declare(queue="campaign_created")

        def callback(ch, method, properties, body):
            try:
                event = json.loads(body)
                logger.info(f"Received campaign event: {event}")

                start_date_str = event["start_date"].replace("Z", "+00:00")
                start_date = timezone.datetime.fromisoformat(start_date_str).date()
                logger.debug(f"Parsed start_date: {start_date}")

                end_date_str = event["end_date"]
                end_date = None
                if end_date_str and end_date_str != "None":
                    end_date = timezone.datetime.fromisoformat(
                        end_date_str.replace("Z", "+00:00")
                    ).date()
                logger.debug(f"Parsed end_date: {end_date}")

                # Save campaign data locally
                logger.info(f"Saving campaign with ID: {event['campaign_id']}")
                campaign, created = Campaign.objects.update_or_create(
                    campaign_id=event["campaign_id"],
                    defaults={
                        "name": event["name"],
                        "description": event["description"],
                        "start_date": start_date,
                        "end_date": end_date,
                        "location": event["location"],
                        "status": event["status"],
                    },
                )
                logger.info(
                    f"Campaign {'created' if created else 'updated'}: {campaign.name}"
                )

                chat_room, chat_created = ChatRoom.objects.get_or_create(
                    campaign=campaign, defaults={"name": f"Chat for {campaign.name}"}
                )
                if chat_created:
                    logger.info(f"Created chat room: {chat_room.name}")
                else:
                    logger.info(
                        f"Chat room already exists for campaign: {campaign.name}"
                    )

            except Exception as e:
                logger.error(f"Error processing campaign event: {e}", exc_info=True)

        channel.basic_consume(
            queue="campaign_created", on_message_callback=callback, auto_ack=True
        )
        logger.info("Waiting for campaign events...")
        channel.start_consuming()

    except Exception as e:
        logger.error(f"Consumer connection failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    consume_campaign_events()
