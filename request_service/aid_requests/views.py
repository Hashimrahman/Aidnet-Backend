from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RequestSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Request
# Create your views here.

class TestAPIView(APIView):
    def get(seld, request):
        return Response({"message":"Hello"})


class RequestAPIView(APIView):
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
    def get(self, request, *args, **kwargs):
        requests = Request.objects.all()
        serializer = RequestSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CancelRequestAPIView(APIView):
    def patch(self, request, pk):
        try:
            requested_item = Request.objects.get(id=pk)
            requested_item.is_cancelled = True
            requested_item.status = "cancelled"
            requested_item.save() 
            return Response({"message": "Request cancelled successfully"}, status=status.HTTP_200_OK)
        
        except Request.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)