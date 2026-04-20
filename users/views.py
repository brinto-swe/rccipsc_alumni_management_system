"""User-facing and admin user views."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import CanManageUsers
from users.selectors import get_admin_user_queryset
from users.serializers import AdminUserUpdateSerializer, UserDetailSerializer


@extend_schema(tags=["Users"], responses=UserDetailSerializer)
class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(UserDetailSerializer(request.user, context={"request": request}).data)


@extend_schema_view(
    list=extend_schema(tags=["Users"]),
    retrieve=extend_schema(tags=["Users"]),
    partial_update=extend_schema(tags=["Users"]),
)
class AdminUserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [CanManageUsers]
    serializer_class = AdminUserUpdateSerializer
    queryset = get_admin_user_queryset()
    search_fields = ["email", "username", "profile__full_name"]
    ordering_fields = ["created_at", "email", "last_login"]
    filterset_fields = ["role", "account_status", "is_active", "is_verified", "managed_batch_year"]

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return UserDetailSerializer
        return super().get_serializer_class()

    @extend_schema(tags=["Users"], request=None, responses=UserDetailSerializer)
    @action(detail=True, methods=["post"])
    def approve(self, request, *args, **kwargs):
        user = self.get_object()
        user.account_status = "active"
        user.is_active = True
        user.save(update_fields=["account_status", "is_active", "updated_at"])
        return Response(UserDetailSerializer(user, context={"request": request}).data)
