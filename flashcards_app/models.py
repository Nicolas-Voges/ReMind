from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="subcategories",
        blank=True,
        null=True,
    )
    shared = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CardType(models.TextChoices):
    SELF_ASSESSMENT = "self_assessment", "Self assessment"
    MULTIPLE_CHOICE = "multiple_choice", "Multiple choice"
    TEXT_INPUT = "text_input", "Text input"


class Flashcard(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="flashcards"
    )
    question = models.TextField()
    answer = models.TextField(blank=True)
    choices = models.JSONField(default=list)
    card_type = models.CharField(
        max_length=20, choices=CardType.choices, default=CardType.SELF_ASSESSMENT
    )
    stage = models.IntegerField(default=1)
    notes = models.TextField(blank=True)
    search_terms = models.JSONField(default=list, blank=True)
    shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, related_name="flashcards", blank=True)

    def __str__(self):
        return f"{self.question[:20]}..."
