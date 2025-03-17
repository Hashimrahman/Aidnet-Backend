from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from rest_framework import serializers

from .models import CustomUser

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.ChoiceField(
        choices=[
            ("affected", "Affected User"),
            ("donor", "Donor"),
            ("volunteer", "Volunteer"),
            ("admin", "Admin"),
        ]
    )
    phone_number = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    organization_name = serializers.CharField(required=False, allow_blank=True)
    skills = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        role = data.get("role")
        if role == "donor" and not data.get("organization_name"):
            raise serializers.ValidationError(
                {"organization_name": "This field is required for donors."}
            )
        if role == "volunteer" and not data.get("skills"):
            raise serializers.ValidationError(
                {"skills": "This field is required for volunteers."}
            )
        return data

    def create(self, validated_data):
        role = validated_data.pop("role")

        user = CustomUser.objects.create_user(**validated_data, role=role)

        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        return user

    def send_verification_email(self, user):
        verification_link = (
            f"http://127.0.0.1:8000/user/verify-email/{user.verification_token}/"
        )
        subject = "Verify Your Email"
        message = f"Click the link to verify your email:\n {verification_link}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(email=email, password=password)
        print(user)
        print(email, password)

        if not user:
            print("hello")
            raise serializers.ValidationError("Invalid credentials")
        if not user.email_verified:
            raise serializers.ValidationError(
                "Email not verified, Please check your inbox"
            )
        if user.is_banned:
            raise serializers.ValidationError("Account is banned")
        
        if not user.is_active:
            raise serializers.ValidationError(
                "User is not active, Please Contact administrator"
            )

        data["user"] = user

        return data


class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        user = self.context["request"].user

        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError("Old Password is Incorrect")

        if data["new_password"] == data["old_password"]:
            raise serializers.ValidationError(
                "Password should be different from the old password"
            )

        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Password Does Not Match")

        return data

    def update_password(self, user):
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
