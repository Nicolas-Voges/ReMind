"""
URL routing configuration for the flashcards API.

This module registers the viewsets for flashcards and categories
with a DefaultRouter and includes the generated patterns.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryModelViewSet, FlashCardModelViewSet

router = DefaultRouter()
router.register(r"flashcards", FlashCardModelViewSet, basename="flashcard")
router.register(r"categories", CategoryModelViewSet, basename="category")

urlpatterns = [
    path('', include(router.urls)),
]
