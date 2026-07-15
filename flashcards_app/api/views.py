from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from flashcards_app.models import Category, Flashcard

from .serializers import (
    BulkAssignCategorySerializer,
    CategoryModelSerializer,
    FlashCardModelSerializer,
)


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

    @action(detail=False, methods=['patch'], url_path='bulk-assign-category')
    def bulk_assign_category(self, request):
        serializer = BulkAssignCategorySerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        category = serializer.validated_data['category_obj']
        cards = serializer.validated_data['cards_queryset']

        for card in cards:
            card.categories.add(category)

        return Response(
            {"message": f"Successfully updated {cards.count()} flashcards."},
            status=status.HTTP_200_OK,
        )


class CategoryModelViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryModelSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Category.objects.filter(user=user).order_by('pk')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
