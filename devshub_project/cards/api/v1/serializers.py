from rest_framework import serializers

from cards import services
from cards.models import Card
from users.api.v1.serializers import UserShortSerializer


class CardListSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    is_saved = serializers.BooleanField(read_only=True)

    class Meta:
        model = Card
        fields = [
            "id",
            "question",
            "created_at",
            "updated_at",
            "is_saved",
            "author",
        ]


class CardDetailSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    is_saved = serializers.BooleanField(read_only=True)

    class Meta:
        model = Card
        fields = [
            "id",
            "question",
            "answer",
            "created_at",
            "updated_at",
            "is_saved",
            "author",
        ]


class CardCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            "id",
            "question",
            "answer",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        return services.create_card(**validated_data)

    def update(self, instance, validated_data):
        return services.update_card(card=instance, **validated_data)
