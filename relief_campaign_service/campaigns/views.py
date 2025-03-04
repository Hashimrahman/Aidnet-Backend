from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from .models import Campaign, CampaignParticipation
from .serializers import CampaignSerializer, CampaignParticipationSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
import requests
import logging
from .tasks import send_leave_notification

logger = logging.getLogger("django")

#Combine get and post (possible views ) - same end point

class CampaignCreateView(APIView):
    def post(self, request):
        serializer = CampaignSerializer(data=request.data)
        if serializer.is_valid():
            campaign = serializer.save()
            campaign.remaining_capacity = campaign.max_capacity
            campaign.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CampaignListView(APIView):
    def get(self, request, *args, **kwargs):
        campaigns = Campaign.objects.all()
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ========================================================== ==========================================================


class CampaignJoinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, campaign_id):
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return Response(
                {"error": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND
            )

        user_id = request.user.id
        role = request.user.role

        # participant_type = request.data.get('participant_type')
        participant_type = role
        if participant_type not in [
            CampaignParticipation.VOLUNTEER,
            CampaignParticipation.AFFECTED,
        ]:
            return Response(
                {
                    "error": "Invalid or missing participant_type. Must be 'volunteer' or 'affected'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if campaign.participations.filter(user_id=user_id).exists():
            return Response(
                {"error": "You have already joined this campaign."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            participation = campaign.join_campaign(user_id, participant_type)
        except ValidationError as e:
            return Response(
                {"error": e.messages if hasattr(e, "messages") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CampaignParticipationSerializer(participation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ========================================================== ==========================================================


class LeaveCampaignView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, campaign_id):
        user_id = request.user.id
        user_email = request.user.email

        campaign = get_object_or_404(Campaign, id=campaign_id)

        participation = campaign.participations.filter(user_id=user_id).first()

        if not participation:
            return Response(
                {"error": "You are not part of this campaign."},
                status=status.HTTP_404_NOT_FOUND,
            )

        campaign.remaining_capacity += 1

        if participation.participant_type == CampaignParticipation.VOLUNTEER:
            campaign.volunteers_registered = max(0, campaign.volunteers_registered - 1)

        campaign.save()
        participation.delete()

        message = f"You have successfully left the campaign: {campaign.name}"
        send_leave_notification(user_email, message)

        return Response(
            {"message": "You have been removed from the campaign successfully."},
            status=status.HTTP_200_OK,
        )


# ========================================================== ==========================================================


# class UserDetailsFetchAPIView(APIView):
#     def get(self, request, *args, **kwargs):
#         user_id = kwargs.get("user_id")
#         url = f"http://user-service:8000/user/user-details/{user_id}"

#         logger.info(f"Requesting user details from: {url}")

#         try:
#             response = requests.get(url, timeout=5)
#             response.raise_for_status()
#         except requests.exceptions.Timeout:
#             logger.error(
#                 f"Timeout occurred while fetching user details for user ID {user_id}"
#             )
#             return Response({"error": "Request timed out"}, status=status.HT3)
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error occurred: {e}")
#             return Response(
#                 {"error": f"Failed to fetch user details: {str(e)}"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if response.status_code == 200:
#             logger.info(f"User data: {response.json()}")
#             return Response(response.json(), status=status.HTTP_200_OK)
#         else:
#             logger.error(
#                 f"Failed to fetch user details, Status Code: {response.status_code}"
#             )
#             return Response(
#                 {"error": f"Failed to fetch user details, {response.status_code}"},
#             )

# class UserDetailsAPIView(APIView):
#     permission_classes = [IsAuthenticated]  # Uses CustomJwtAuthentication
#     def get(self, request):
#         logger.info(f"Received Authorization header: {request.headers.get('Authorization')}")
#         user = request.user  # Populated from RabbitMQ-based authentication
#         return Response({
#             "id": user.id,
#             "email": user.email,
#             "role": user.role,
#             "is_authenticated": user.is_authenticated
#         })
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import logging
from django.contrib.auth.models import AnonymousUser
logger = logging.getLogger(__name__)

class UserDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"Received Authorization header: {request.headers.get('Authorization')}")
        user = request.user  # Populated from RabbitMQ-based authentication
        
        if isinstance(user, AnonymousUser):
            return Response({"error": "User not authenticated"}, status=401)

        return Response({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            # "is_authenticated": True
        })



# ========================================================== ==========================================================


class UpdateCampaignStatuAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, id=campaign_id)

        if campaign.organizer != request.user.id and request.user.role != "admin":
            return Response(
                {"details": "You are not authorized for this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        campaign.status = "ended"
        campaign.end_date = timezone.now()
        campaign.save()

        return Response(
            {
                "message": f"Campaign ${campaign.name} has been ended on {campaign.end_date}"
            },
            status=status.HTTP_200_OK,
        )


# ========================================================== ==========================================================


class UserCampaignsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user_id = request.user.id
        participation = CampaignParticipation.objects.filter(user_id=user_id)
        campaigns = Campaign.objects.filter(id__in=participation.values("campaign_id"))
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ========================================================== ==========================================================
