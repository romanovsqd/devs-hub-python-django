from urllib.parse import quote

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cards import services
from core.permissions import IsAuthorOrReadOnly

from .serializers import (
    CardCreateUpdateSerializer,
    CardDetailSerializer,
    CardListSerializer,
)


class CardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        if self.action in ["list", "retrieve", "toggle_save"]:
            return services.get_cards_with_saved_status(user=user)
        return services.get_cards()

    def get_serializer_class(self):
        if self.action == "list":
            return CardListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return CardCreateUpdateSerializer
        return CardDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def toggle_save(self, request, pk):
        card = self.get_object()
        is_saved, message = services.toggle_card_save_by_user(
            card=card, user=request.user
        )
        return Response({"is_saved": is_saved, "message": message})

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def export(self, request, pk):
        card = services.get_card_created_or_saved_by_user(card_id=pk, user=request.user)
        filename, content = services.generate_card_data_for_export(card=card)

        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = (
            "attachment; " f"filename*=UTF-8''{quote(filename)}"
        )

        return response
