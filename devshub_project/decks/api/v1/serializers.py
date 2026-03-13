from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from cards.api.v1.serializers import CardShortSerializer
from cards.models import Card
from cards.services import get_cards_created_or_saved_by_user
from decks import services
from decks.models import Deck
from users.api.v1.serializers import UserShortSerializer


class DeckListSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    is_saved = serializers.BooleanField(read_only=True)
    in_study = serializers.SerializerMethodField()

    class Meta:
        model = Deck
        fields = [
            "id",
            "title",
            "author",
            "is_saved",
            "in_study",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.context.get("studying_ids", False):
            self.fields.pop("in_study", None)

    def get_in_study(self, deck):
        studying_ids = self.context.get("studying_ids", set())
        return deck.id in studying_ids


class DeckDetailSerializer(serializers.ModelSerializer):
    cards = serializers.SerializerMethodField()
    author = UserShortSerializer(read_only=True)
    is_saved = serializers.BooleanField(read_only=True)

    class Meta:
        model = Deck
        fields = [
            "id",
            "title",
            "cards",
            "is_saved",
            "author",
            "created_at",
            "updated_at",
        ]

    def get_cards(self, obj):
        request = self.context["request"]

        user = request.user if request.user.is_authenticated else None
        cards = services.get_deck_cards_with_saved_status(deck=obj, user=user)
        return CardShortSerializer(cards, many=True).data


class DeckCreateUpdateSerializer(serializers.ModelSerializer):
    cards = PrimaryKeyRelatedField(many=True, queryset=Card.objects.none())

    class Meta:
        model = Deck
        fields = [
            "id",
            "title",
            "cards",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context["request"].user
        self.fields["cards"].child_relation.queryset = (
            get_cards_created_or_saved_by_user(user=user)
        )

    def create(self, validated_data):
        return services.create_deck(**validated_data)

    def update(self, instance, validated_data):
        return services.update_deck(deck=instance, **validated_data)
