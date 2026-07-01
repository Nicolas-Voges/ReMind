from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from flashcards_app.models import Flashcard

from .serializers import FlashCardModelSerializer


class FlashCardModelViewSet(viewsets.ModelViewSet):
    serializer_class = FlashCardModelSerializer

    def get_queryset(self):
        user = self.request.user
        return Flashcard.objects.filter(user=user)

    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
