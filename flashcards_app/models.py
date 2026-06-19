from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subcategories',
        blank=True,
        null=True
    )
    shared = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Flashcard(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='flashcards',
        null=True,
    )
    question = models.TextField()
    answer = models.TextField()
    stage = models.IntegerField(default=1)
    notes = models.TextField(blank=True)
    search_terms = models.JSONField(default=list, blank=True)
    shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    due_date = models.DateTimeField(auto_now_add=True, null=True)  
    categories = models.ManyToManyField(
        Category, 
        related_name='flashcards', 
        blank=True
    )

    def __str__(self):
        return f"{self.question[:20]}..."