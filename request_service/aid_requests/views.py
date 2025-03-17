from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RequestSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class TestAPIView(APIView):
    def get(seld, request):
        return Response({"message":"Hello"})


class CreateRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request,*args, **kwargs):
        data = request.data
        data["requested_user_id"] = request.user.id
        
        seriliazer = RequestSerializer(data=data)
        if seriliazer.is_valid():
            seriliazer.save()
            return Response(
                {"message":"Request created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(seriliazer.errors, status=status.HTTP_400_BAD_REQUEST)