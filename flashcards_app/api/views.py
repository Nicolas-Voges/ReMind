from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from flashcards_app.models import Category, Flashcard

from .serializers import CategoryModelSerializer, FlashCardModelSerializer


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 100


class FlashCardModelViewSet(viewsets.ModelViewSet):
    serializer_class = FlashCardModelSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Flashcard.objects.filter(user=user).order_by('pk')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryModelViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryModelSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Category.objects.filter(user=user).order_by('pk')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
