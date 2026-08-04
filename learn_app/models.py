from django.conf import settings
from django.db import models
from django.utils import timezone

from flashcards_app.models import Category, Flashcard


class LogReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_logs"
    )
    flashcard = models.ForeignKey(
        Flashcard, on_delete=models.CASCADE, related_name="review_logs"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="review_logs"
    )
    was_correct = models.BooleanField()
    last_interval_ms = models.BigIntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-created_at",)

        indexes = (
            models.Index(fields=("last_interval_ms", "was_correct")),
            models.Index(fields=("category", "-created_at")),
            models.Index(fields=("flashcard", "-created_at")),
            models.Index(fields=("user", "-created_at")),
        )

    def __str__(self):
        status = "correct" if self.was_correct else "wrong"
        return f"{self.user.username} - Card {self.flashcard_id}: {status} ({self.created_at.date()})"
