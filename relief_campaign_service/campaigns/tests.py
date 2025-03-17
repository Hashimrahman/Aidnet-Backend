from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Campaign, CampaignParticipation


class CampaignAPITestCase(TestCase):
    def setUp(self):
        """Initialize test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            description="This is a test campaign",
            max_capacity=10,
            remaining_capacity=10,
        )

    def test_create_campaign(self):
        """Test Campaign Creation API"""
        data = {
            "name": "New Campaign",
            "description": "Campaign Description",
            "max_capacity": 15,
        }
        response = self.client.post("/campaigns/create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Campaign")

    def test_list_campaigns(self):
        """Test retrieving all campaigns"""
        response = self.client.get("/campaigns/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_join_campaign(self):
        """Test joining a campaign"""
        data = {"participant_type": "volunteer"}
        response = self.client.post(
            f"/campaigns/{self.campaign.id}/join/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_leave_campaign(self):
        """Test leaving a campaign"""
        CampaignParticipation.objects.create(
            campaign=self.campaign, user_id=self.user.id, participant_type="volunteer"
        )

        response = self.client.delete(
            f"/campaigns/{self.campaign.id}/leave/{self.user.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("requests.get")
    def test_fetch_user_details(self, mock_get):
        """Test user details API call with mocked response"""
        mock_response = {"id": self.user.id, "username": self.user.username}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = self.client.get(f"/user-details/{self.user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
