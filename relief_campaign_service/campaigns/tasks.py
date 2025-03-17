import requests
from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_leave_notification(email, message):
    if email:
        send_mail(
            subject="Campaign Update",
            message=message,
            from_email="hashimrhmnp@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )

    return "Notification Sent"
