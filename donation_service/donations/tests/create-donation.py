from django.contrib.auth.models import User
from django.urls import reverse
from donations.models import Donation
from rest_framework import status
from rest_framework.test import APITestCase


class DonationCreateAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

        self.create_donation_url = reverse("donate")

    def test_create_donation_success(self):
        self.client.force_authenticate(user=self.user)

        data = {
            "type": "Food",
            "quantity": 100,
            "description": "Water Can",
            "delivery_method": "Pickup",
            "relief_campaign_id": None,
        }

        response = self.client.post(self.create_donation_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Donation.objects.count(), 1)
        self.assertEqual(Donation.objects.first().type, "Food")
        self.assertEqual(Donation.objects.first().donor_id, self.user.id)

    def test_create_donation_invalid_data(self):
        self.client.force_authenticate(user=self.user)

        data = {"description": "Water Can"}

        response = self.client.post(self.create_donation_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Donation.objects.count(), 0)

    def test_create_donation_unauthenticated(self):
        self.client.logout()

        data = {
            "type": "Food",
            "quantity": 10,
            "description": "Canned food items",
            "delivery_method": "Pickup",
            "relief_campaign_id": None,
        }

        response = self.client.post(self.create_donation_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Donation.objects.count(), 0)
