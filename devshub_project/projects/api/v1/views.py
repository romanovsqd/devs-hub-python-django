from rest_framework import viewsets

from core.permissions import IsAuthorOrReadOnly
from projects import services

from .serializers import (
    ProjectCreateUpdateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = services.get_projects()
    permission_classes = [IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
