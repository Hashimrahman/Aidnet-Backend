from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, IntegrityError
from .models import CustomUser
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer,PasswordResetSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin

User = get_user_model()


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if user:
           print("hi")
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.create(serializer.validated_data)

                    serializer.send_verification_email(user)

                    return Response(
                        {
                            "message": "User registered successfully. Please check your email to verify your account."
                        },
                        status=status.HTTP_201_CREATED,
                    )

            except IntegrityError as e:
                return Response(
                    {"error": "A user with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"error": f"An unexpected error occurred: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========================================================== ==========================================================

class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            user = CustomUser.objects.get(verification_token=token)
            if not user.email_verified:
                user.email_verified = True
                user.is_active = True
                user.save()
                return Response(
                    {"message": "Email verified successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Email already verified."}, status=status.HTTP_200_OK
                )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Invalid verification token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

# ========================================================== ==========================================================

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        print("Hello login test")
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response(
                {
                    "message": "Login successful1",
                    "access_token": access_token,
                    "refresh_token": str(refresh),
                    "user": {
                        "email": user.email,
                        "role": user.role,
                        "phone_number": user.phone_number,
                        "userId": user.id,
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# ========================================================== ==========================================================

class ListUsersAPIView(ListAPIView):

    permission_classes = [IsAdmin]
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

# ========================================================== ==========================================================

class UserDetailView(APIView):
    def get(self, request, id, *args, **kwargs):
        try:
            user = User.objects.get(id=id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

# ========================================================== ==========================================================

class DeleteUserAPIView(APIView):
    permission_classes = [IsAdmin]
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response(
                {"message": "User deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

# ========================================================== ==========================================================

class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data, context={'request':request})

        if serializer.is_valid():
            serializer.update_password(request.user)
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# ========================================================== ==========================================================

class GetUserView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            return Response({"id": user.id, "role": user.role}, status=200)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

# ========================================================== ==========================================================