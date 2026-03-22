from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from cards import services as card_services
from cards.api.v1.serializers import CardListSerializer
from core.permissions import IsOwner
from decks import services as deck_services
from decks.api.v1.serializers import DeckListSerializer
from projects import services as project_services
from projects.api.v1.serializers import ProjectListSerializer
from repetitions import services as repetition_services
from users import services

from .serializers import (
    UserDetailSerializer,
    UserListSerializer,
    UserRegisterSerializer,
    UserShortSerializer,
    UserUpdateSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserShortSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "put", "patch"]
    lookup_field = "username"

    def get_queryset(self):
        return services.get_users()

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticatedOrReadOnly()]

    def get_object(self):
        if self.action == "retrieve":
            username = self.kwargs["username"]
            return services.get_user_with_codewars_profile(username=username)
        return super().get_object()

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserDetailSerializer

    @action(detail=True)
    def cards(self, request, username):
        user = self.get_object()
        current_user = request.user if request.user.is_authenticated else None
        user_cards = card_services.get_user_cards_with_saved_status(
            user=user, current_user=current_user
        )

        serializer = CardListSerializer(user_cards, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def decks(self, request, username):
        user = self.get_object()
        current_user = request.user if request.user.is_authenticated else None
        studying_ids = repetition_services.get_studying_decks_ids(user=user)

        user_decks = deck_services.get_user_decks_with_saved_status(
            user=user,
            current_user=current_user,
        )

        serializer = DeckListSerializer(
            user_decks, many=True, context={"studying_ids": studying_ids}
        )
        return Response(serializer.data)

    @action(detail=True)
    def projects(self, request, username):
        user = self.get_object()
        user_projects = project_services.get_projects_created_by_user(user=user)

        serializer = ProjectListSerializer(user_projects, many=True)
        return Response(serializer.data)
