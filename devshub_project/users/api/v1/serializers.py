from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from cards import services as card_services
from decks import services as deck_services
from projects import services as project_services
from users import services
from users.models import CodewarsProfile

User = get_user_model()


class CodewarsProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodewarsProfile
        fields = ["honor", "leaderboard_position", "total_completed_katas", "languages"]


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "specialization",
            "skills",
            "codewars_username",
            "avatar",
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    codewars_profile = CodewarsProfileSerializer(read_only=True)
    cards_stats = serializers.SerializerMethodField()
    decks_stats = serializers.SerializerMethodField()
    projects_stats = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "specialization",
            "skills",
            "avatar",
            "codewars_username",
            "codewars_profile",
            "cards_stats",
            "decks_stats",
            "projects_stats",
        ]

    def get_cards_stats(self, user):
        return card_services.get_cards_stats(user=user)

    def get_decks_stats(self, user):
        return deck_services.get_decks_stats(user=user)

    def get_projects_stats(self, user):
        return project_services.get_projects_stats(user=user)


class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="Этот email уже занят")
        ]
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "specialization",
            "skills",
            "codewars_username",
            "avatar",
        ]

    def update(self, instance, validated_data):
        return services.update_user(user=instance, **validated_data)


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]
