# import json
# import logging

# import aiohttp
# from channels.db import database_sync_to_async
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.contrib.auth.models import AnonymousUser

# from .models import ChatRoom, Message

# logger = logging.getLogger("django")

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.campaign_id = self.scope["url_route"]["kwargs"]["campaign_id"]
#         self.room_group_name = f"chat_{self.campaign_id}"
#         logger.info(f"Connecting to campaign: {self.campaign_id}")

#         query_string = self.scope.get("query_string", b"").decode()
#         logger.info(f"Subprotocols received: {self.scope['subprotocols'][0]}")

#         # token = dict(q.split("=") for q in query_string.split("&") if "=" in q).get("token", None)
#         token = None
#         if self.scope["subprotocols"]:
#             token = self.scope["subprotocols"][0]
#         logger.info(f"Token received: {token}")
#         logger.info(f"Query received: {query_string}")

#         if token:
#             user_data = await self.validate_token(token)
#             if user_data:
#                 self.scope["user"] = type("User", (), {
#                     "id": user_data["id"],
#                     "full_name": user_data["full_name"],
#                     "is_authenticated": True
#                 })()
#                 logger.info(f"User authenticated: {user_data['id']} - {user_data['full_name']}")
#             else:
#                 self.scope["user"] = AnonymousUser()
#                 logger.warning("Invalid token, user set as anonymous")
#         else:
#             self.scope["user"] = AnonymousUser()
#             logger.warning("No token provided, user set as anonymous")

#         try:
#             await database_sync_to_async(ChatRoom.objects.get)(campaign__campaign_id=self.campaign_id)
#             await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#             await self.accept()
#             logger.info("WebSocket connection accepted")

#             logger.info("Fetching message history")
#             messages = await self.get_message_history()
#             logger.info(f"Messages retrieved: {type(messages)} - {messages}")
#             for msg in messages:
#                 logger.info(f"Sending message: {msg.content} from user {msg.user_id}")
#                 await self.send(
#                     text_data=json.dumps({
#                         "message": msg.content,
#                         "user_id": msg.user_id,
#                         "user_name": msg.user_name,
#                     })
#                 )
#         except ChatRoom.DoesNotExist:
#             logger.error(f"No ChatRoom for campaign_id: {self.campaign_id}")
#             await self.close(code=4000)
#         except Exception as e:
#             logger.error(f"Connect error: {e}", exc_info=True)
#             await self.close(code=4001)

#     async def validate_token(self, token):
#         async with aiohttp.ClientSession() as session:
#             async with session.get(
#                 "http://user-service:8000/user/verify-token/",
#                 headers={"Authorization": f"Bearer {token}"}
#             ) as response:
#                 if response.status == 200:
#                     return await response.json()
#                 logger.error(f"Token validation failed: {response.status}")
#                 return None

#     @database_sync_to_async
#     def get_message_history(self):
#         chat_room = ChatRoom.objects.get(campaign__campaign_id=self.campaign_id)
#         # messages = chat_room.messages.order_by("timestamp")[:50]
#         messages = list(chat_room.messages.order_by("timestamp")[:50])
#         logger.info(f"Returning {len(messages)} messages from get_message_history")
#         return messages

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
#         logger.info(f"Disconnected with code: {close_code}")

#     async def receive(self, text_data):
#         try:
#             logger.info(f"Received data: {text_data}")
#             text_data_json = json.loads(text_data)
#             message = text_data_json["message"]
#             user = self.scope.get("user", AnonymousUser())
#             logger.info(f"User scope: {user}, Is authenticated: {user.is_authenticated}")
#             user_id = user.id if user.is_authenticated else -1
#             user_name = user.full_name if user.is_authenticated else "Anonymous"
#             logger.info(f"Using user_id: {user_id}, user_name: {user_name}")

#             chat_room = await database_sync_to_async(ChatRoom.objects.get)(
#                 campaign__campaign_id=self.campaign_id
#             )
#             await database_sync_to_async(Message.objects.create)(
#                 chat_room=chat_room,
#                 user_id=user_id,
#                 user_name=user_name,
#                 content=message
#             )
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     "type": "chat_message",
#                     "message": message,
#                     "user_id": user_id,
#                     "user_name": user_name,
#                 },
#             )
#         except KeyError as e:
#             logger.error(f"Invalid message format: {e}")
#             await self.send(
#                 text_data=json.dumps({"error": "Message must include 'message' key"})
#             )
#         except ChatRoom.DoesNotExist:
#             logger.error(f"ChatRoom not found for campaign_id: {self.campaign_id}")
#             await self.send(text_data=json.dumps({"error": "Chat room not found"}))
#         except Exception as e:
#             logger.error(f"Receive error: {e}", exc_info=True)
#             await self.close(code=4002)

#     async def chat_message(self, event):
#         try:
#             await self.send(
#                 text_data=json.dumps({
#                     "message": event["message"],
#                     "user_id": event["user_id"],
#                     "user_name": event["user_name"],
#                 })
#             )
#         except Exception as e:
#             logger.error(f"Chat_message error: {e}", exc_info=True)


import json
import logging

import aiohttp
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from .models import ChatRoom, Message

logger = logging.getLogger("django")


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.campaign_id = self.scope["url_route"]["kwargs"]["campaign_id"]
        self.room_group_name = f"chat_{self.campaign_id}"
        logger.info(f"Connecting to campaign: {self.campaign_id}")

        # Initially set user as anonymous
        self.scope["user"] = AnonymousUser()
        logger.info("User set as anonymous until authenticated")

        try:
            await database_sync_to_async(ChatRoom.objects.get)(
                campaign__campaign_id=self.campaign_id
            )
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            logger.info("WebSocket connection accepted")

            # Optionally send a welcome message or instructions
            await self.send(
                text_data=json.dumps(
                    {
                        "message": "Connected. Please send your authentication token.",
                        "type": "info",
                    }
                )
            )
        except ChatRoom.DoesNotExist:
            logger.error(f"No ChatRoom for campaign_id: {self.campaign_id}")
            await self.close(code=4000)
        except Exception as e:
            logger.error(f"Connect error: {e}", exc_info=True)
            await self.close(code=4001)

    async def validate_token(self, token):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://user-service:8000/user/verify-token/",
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Token validation failed: {response.status}")
                return None

    @database_sync_to_async
    def get_message_history(self):
        chat_room = ChatRoom.objects.get(campaign__campaign_id=self.campaign_id)
        messages = list(chat_room.messages.order_by("timestamp")[:50])
        logger.info(f"Returning {len(messages)} messages from get_message_history")
        return messages

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"Disconnected with code: {close_code}")

    async def receive(self, text_data):
        try:
            logger.info(f"Received data: {text_data}")
            text_data_json = json.loads(text_data)

            if text_data_json.get("type") == "auth":
                token = text_data_json.get("token")
                if not token:
                    await self.send(
                        text_data=json.dumps({"error": "No token provided"})
                    )
                    return
                user_data = await self.validate_token(token)
                if user_data:
                    self.scope["user"] = type(
                        "User",
                        (),
                        {
                            "id": user_data["id"],
                            "full_name": user_data["full_name"],
                            "is_authenticated": True,
                        },
                    )()
                    logger.info(
                        f"User authenticated: {user_data['id']} - {user_data['full_name']}"
                    )
                    messages = await self.get_message_history()
                    for msg in messages:
                        await self.send(
                            text_data=json.dumps(
                                {
                                    "message": msg.content,
                                    "user_id": msg.user_id,
                                    "user_name": msg.user_name,
                                }
                            )
                        )
                    # await self.send(text_data=json.dumps({"message": "Authentication successful"}))
                else:
                    logger.warning("Invalid token")
                    await self.send(text_data=json.dumps({"error": "Invalid token"}))
                return

            # Handle regular chat messages (only if authenticated, optional)
            if not self.scope["user"].is_authenticated:
                await self.send(text_data=json.dumps({"error": "Not authenticated"}))
                return

            message = text_data_json["message"]
            user = self.scope["user"]
            user_id = user.id
            user_name = user.full_name

            chat_room = await database_sync_to_async(ChatRoom.objects.get)(
                campaign__campaign_id=self.campaign_id
            )
            await database_sync_to_async(Message.objects.create)(
                chat_room=chat_room,
                user_id=user_id,
                user_name=user_name,
                content=message,
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "user_id": user_id,
                    "user_name": user_name,
                },
            )
        except KeyError as e:
            logger.error(f"Invalid message format: {e}")
            await self.send(
                text_data=json.dumps({"error": "Message must include 'message' key"})
            )
        except ChatRoom.DoesNotExist:
            logger.error(f"ChatRoom not found for campaign_id: {self.campaign_id}")
            await self.send(text_data=json.dumps({"error": "Chat room not found"}))
        except Exception as e:
            logger.error(f"Receive error: {e}", exc_info=True)
            await self.close(code=4002)

    async def chat_message(self, event):
        try:
            await self.send(
                text_data=json.dumps(
                    {
                        "message": event["message"],
                        "user_id": event["user_id"],
                        "user_name": event["user_name"],
                    }
                )
            )
        except Exception as e:
            logger.error(f"Chat_message error: {e}", exc_info=True)
