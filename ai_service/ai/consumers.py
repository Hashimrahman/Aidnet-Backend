# # ai_service/ai/consumers.py
# import json
# import logging
# import google.generativeai as genai
# from channels.generic.websocket import AsyncWebsocketConsumer

# logger = logging.getLogger("django")

# # Configure Gemini API (use environment variable in production)
# genai.configure(api_key="AIzaSyCy2oq7Gn-ZRvyvwoA90EswHf7wz0O3ngk")  # Replace with os.getenv("GEMINI_API_KEY")

# class AIChatConsumer(AsyncWebsocketConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.model = genai.GenerativeModel('gemini-1.5-flash')
#         self.chat = None

#     async def connect(self):
#         # Start a new chat session for each connection
#         self.chat = self.model.start_chat(history=[])
#         await self.accept()
#         logger.info("AI Chat WebSocket connected")
#         await self.send(text_data=json.dumps({
#             "message": "Hello! How can I assist you today?",
#             "sender": "bot"
#         }))

#     async def disconnect(self, close_code):
#         logger.info(f"AI Chat WebSocket disconnected with code: {close_code}")

#     async def receive(self, text_data):
#         try:
#             data = json.loads(text_data)
#             user_message = data.get("message")
#             if not user_message:
#                 await self.send(text_data=json.dumps({
#                     "message": "Please send a message.",
#                     "sender": "bot"
#                 }))
#                 return

#             logger.info(f"Received user message: {user_message}")
#             response = self.chat.send_message(user_message)
#             await self.send(text_data=json.dumps({
#                 "message": response.text,
#                 "sender": "bot"
#             }))
#         except Exception as e:
#             logger.error(f"Error in AI chat: {e}")
#             await self.send(text_data=json.dumps({
#                 "message": "Sorry, something went wrong.",
#                 "sender": "bot"
#             }))


import json
import logging
import google.generativeai as genai
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger("django")

# genai.configure(api_key=os.getenv("GEMINI_API_KEY", "your_key_here"))
genai.configure(api_key="AIzaSyCy2oq7Gn-ZRvyvwoA90EswHf7wz0O3ngk")


class AIChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.chat = None
    async def connect(self):
        logger.info("AI Chat WebSocket connected - Starting chat session")
        try:
            self.chat = self.model.start_chat(history=[])
            logger.info("Chat session started")
            await self.accept()
            logger.info("WebSocket accepted")
            await self.send(
                text_data=json.dumps(
                    {"message": "Hello! How can I assist you today?", "sender": "bot"}
                )
            )
            logger.info("Initial message sent")
        except Exception as e:
            logger.error(f"Error in connect: {e}", exc_info=True)
            await self.send(text_data=json.dumps({"message": "Connection failed.", "sender": "bot"}))
            await self.close(code=4000)

    async def disconnect(self, close_code):
        logger.info(f"AI Chat WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data):
        try:
            logger.info(f"Received raw data: {text_data}")
            data = json.loads(text_data)
            user_message = data.get("message")
            if not user_message:
                await self.send(
                    text_data=json.dumps(
                        {"message": "Please send a message.", "sender": "bot"}
                    )
                )
                return

            response = self.chat.send_message(user_message)
            await self.send(
                text_data=json.dumps({"message": response.text, "sender": "bot"})
            )
        except Exception as e:
            logger.error(f"Error in receive: {e}", exc_info=True)
            await self.send(
                text_data=json.dumps(
                    {"message": "Sorry, something went wrong.", "sender": "bot"}
                )
            )
