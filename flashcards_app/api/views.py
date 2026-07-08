from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from flashcards_app.models import Flashcard

from .serializers import FlashCardModelSerializer


class FlashcardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 100


class FlashCardModelViewSet(viewsets.ModelViewSet):
    serializer_class = FlashCardModelSerializer
    pagination_class = FlashcardPagination

    def get_queryset(self):
        user = self.request.user
        return Flashcard.objects.filter(user=user).order_by('pk')

    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
