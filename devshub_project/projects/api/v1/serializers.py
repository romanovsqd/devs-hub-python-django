from rest_framework import serializers

from projects import services
from projects.models import Project, ProjectImage
from users.api.v1.serializers import UserShortSerializer


class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ["id", "file"]


class ProjectListSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "repository_url",
            "live_url",
            "cover_image",
            "created_at",
            "updated_at",
            "author",
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True,
        allow_empty=True,
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "repository_url",
            "live_url",
            "images",
            "cover_image",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        return services.create_project(**validated_data)

    def update(self, instance, validated_data):
        return services.update_project(project=instance, **validated_data)
