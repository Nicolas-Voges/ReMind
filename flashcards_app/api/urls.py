from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryModelViewSet, FlashCardModelViewSet

router = DefaultRouter()
router.register(r"flashcards", FlashCardModelViewSet, basename="flashcard")
router.register(r"categories", CategoryModelViewSet, basename="category")

urlpatterns = [
    path('', include(router.urls)),
]
