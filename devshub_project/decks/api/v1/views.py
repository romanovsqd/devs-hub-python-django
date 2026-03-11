from urllib.parse import quote

from django.http import StreamingHttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsAuthorOrReadOnly
from decks import services

from .serializers import (
    DeckCreateUpdateSerializer,
    DeckDetailSerializer,
    DeckListSerializer,
)


class DeckViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        if self.action in ["list", "retrieve", "toggle_save"]:
            return services.get_decks_with_saved_status(user=user)
        return services.get_decks()

    def get_serializer_class(self):
        if self.action == "list":
            return DeckListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return DeckCreateUpdateSerializer
        return DeckDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def toggle_save(self, request, pk):
        deck = self.get_object()
        is_saved, result = services.toggle_deck_save_by_user(
            deck=deck, user=request.user
        )
        return Response({"is_saved": is_saved, "message": result})

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def export(self, request, pk):
        deck = services.get_deck_created_or_saved_by_user(deck_id=pk, user=request.user)
        filename, cards_generator = services.prepare_deck_for_export(deck=deck)

        response = StreamingHttpResponse(
            cards_generator, content_type="text/plain; charset=utf-8"
        )
        response["Content-Disposition"] = (
            "attachment; " f"filename*=UTF-8''{quote(filename)}"
        )

        return response
