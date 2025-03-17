from django.db import models

class Request(models.Model):
    URGENCY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]

    REQUEST_TYPE_CHOICES = [
        ("food", "Food"),
        ("medical", "Medical Aid"),
        ("shelter", "Shelter"),
        ("clothing", "Clothing"),
        ("volunteering", "Volunteering"),
        ("other", "Other"),
    ]

    requested_user_id = models.IntegerField()
    location = models.CharField(max_length=255)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    urgency_level = models.CharField(max_length=10, choices=URGENCY_CHOICES, default="medium")
    details = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.id} - {self.request_type} - {self.urgency_level} ({self.status})"

    class Meta:
        ordering = ["-created_at"]
