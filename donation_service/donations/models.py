from django.db import models
import requests

class Donation(models.Model):
    
    class DeliveryMethod(models.TextChoices):
        PICKUP = 'Pickup', 'Available For Pickup'
        DELIVERED = 'Delivered', 'Will be delivered by Donor'
    
    class Status(models.TextChoices):
        AVAILABLE = 'Available','Available'
        DELIVERED = 'Delivered'
    
    type = models.CharField(max_length=200)
    donor_id = models.IntegerField()
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    delivery_method = models.CharField(max_length=10, choices=DeliveryMethod.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)
    relief_campaign_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_donor(donor_id):
        try:
            response = requests.get(f"http://user-service:8000/user/user-details/{donor_id}")
            if response.status_code == 200:
                return response.json().get("name", "UnKnown")
        except requests.exceptions.RequestException as e:
            return "Unknown"
        return "Unknown"
    
    def __str__(self):
        donor_name = self.get_donor(self.donor_id)
        return f"{self.type} (Donor: {donor_name}) - {self.get_status_display()}"