"""
Database models for the flashcards application.

Defines the structure for categories (including hierarchical trees)
and flashcards with varying study formats and scheduling metadata.
"""

from django.conf import settings
from django.db import models


class Category(models.Model):
    """
    Represents a user-defined category for grouping flashcards.

    Supports a hierarchical structure via a self-referential foreign key
    to allow multi-level subcategories.
    """

    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name="subcategories",
        blank=True,
        null=True,
    )

    class Meta:
        indexes = (models.Index(fields=("user", "parent")),)

    def __str__(self):
        return self.name


class DifficultyRating(models.TextChoices):
    VERY_HARD = "very_hard", "Very hard"
    HARD = "hard", "Hard"
    MEDIUM = "medium", "Medium"
    EASY = "easy", "Easy"
    VERY_EASY = "very_easy", "Very easy"


class CardType(models.TextChoices):
    """Available study formats for flashcards."""

    SELF_ASSESSMENT = "self_assessment", "Self assessment"
    MULTIPLE_CHOICE = "multiple_choice", "Multiple choice"
    TEXT_INPUT = "text_input", "Text input"


class Flashcard(models.Model):
    """
    Represents an individual flashcard item owned by a user.

    Stores content fields, format configuration, and tracking parameters
    required for spaced repetition algorithms.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="flashcards"
    )
    question = models.TextField()
    answer = models.TextField(blank=True)
    choices = models.JSONField(default=list)
    card_type = models.CharField(
        max_length=20, choices=CardType.choices, default=CardType.SELF_ASSESSMENT
    )
    notes = models.TextField(blank=True)
    search_terms = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_interval_ms = models.BigIntegerField(default=0)
    due_date = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, related_name="flashcards", blank=True)
    difficulty = models.CharField(
        max_length=10, choices=DifficultyRating.choices, default=DifficultyRating.MEDIUM
    )

    class Meta:
        ordering = ("-created_at",)

        indexes = (
            models.Index(fields=('user', 'due_date')),
            models.Index(fields=('user', '-created_at')),
            models.Index(fields=('user', 'last_interval_ms')),
        )

    def __str__(self):
        return f"{self.question[:20]}..."
