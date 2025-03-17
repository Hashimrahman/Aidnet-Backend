from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Donation
from .serializer import DonationSerializer


class TestAPI(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Testing New Service"}, status=status.HTTP_200_OK)


class DonationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        donor_id = request.user.id
        request.data["donor_id"] = donor_id
        serializer = DonationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllDonationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        donations = Donation.objects.all()
        serializer = DonationSerializer(donations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DonorDonationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        donor = request.user
        if donor.role == "donor":
            donations = Donation.objects.filter(donor_id=donor.id)
            serializer = DonationSerializer(donations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return {"message": "User is not a donor"}


class DonationDetailedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        try:
            donation = Donation.objects.get(id=id)
            serializer = DonationSerializer(donation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Donation.DoesNotExist:
            return Response(
                {"Details": "Donation Not Found"}, status=status.HTTP_404_NOT_FOUND
            )


class DeleteDonationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, donation_id):
        try:
            donation = Donation.objects.get(id=donation_id, donor_id=request.user.id)
            donation.delete()
            return Response(
                {"message": f"Donation with id {donation_id} has been deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Donation.DoesNotExist:
            return Response(
                {"error": "Donation not found or not authorized"},
                status=status.HTTP_404_NOT_FOUND,
            )


class UpdateDonationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, donation_id):
        try:
            donation = Donation.objects.get(id=donation_id, donor_id=request.user.id)
        except Donation.DoesNotExist:
            return Response(
                {"error": "Donation not found or not authorized"},
                status=status.HTTP_404_NOT_FOUND,
            )
        request.data["donor_id"] = request.user.id
        serializer = DonationSerializer(donation, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
