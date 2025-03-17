import uuid

from django.db import models


class Campaign(models.Model):
    campaign_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=255)
    location = models.CharField(max_length=55)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.OneToOneField(
        Campaign, on_delete=models.CASCADE, related_name="chat_room"
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=150, default="Unknown")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user_id} in {self.chat_room.name}"
