"""Authentication serializers and Djoser extensions."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import AccountAuditLog
from users.enums import AccountStatus, UserRole
from users.services import validate_user_can_login


User = get_user_model()


class AccountRegistrationSerializer(UserCreateSerializer):
    full_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    batch_year = serializers.IntegerField(required=False)
    academic_group = serializers.CharField(required=False, allow_blank=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "password",
            "re_password",
            "username",
            "role",
            "full_name",
            "phone_number",
            "batch_year",
            "academic_group",
        )
        extra_kwargs = {"role": {"required": False}}

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs.setdefault("role", UserRole.ALUMNI)
        return attrs

    def validate_role(self, value):
        if value not in {UserRole.ALUMNI, UserRole.GUEST}:
            raise serializers.ValidationError(
                "Public registration is limited to alumni and guest/current-student roles."
            )
        return value

    def create(self, validated_data):
        profile_payload = {
            "full_name": validated_data.pop("full_name", ""),
            "phone_number": validated_data.pop("phone_number", ""),
            "batch_year": validated_data.pop("batch_year", None),
            "academic_group": validated_data.pop("academic_group", ""),
        }
        validated_data["account_status"] = AccountStatus.PENDING
        user = super().create(validated_data)
        if hasattr(user, "profile"):
            for field, value in profile_payload.items():
                if value not in ("", None):
                    setattr(user.profile, field, value)
            user.profile.save()
        return user


class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs["email"].lower()
        password = attrs["password"]

        user = User.objects.filter(email__iexact=email).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError("No active account found with the given credentials.")

        validate_user_can_login(user)
        self.user = user

        refresh = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        token = RefreshToken(self.validated_data["refresh"])
        token.blacklist()


class AccountAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountAuditLog
        fields = "__all__"
