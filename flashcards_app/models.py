from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Flashcard(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='flashcards'
    )
    question = models.TextField()
    answer = models.TextField()
    stage = models.IntegerField(default=1)
    
    categories = models.ManyToManyField(
        Category, 
        related_name='flashcards', 
        blank=True
    )

    def __str__(self):
        return f"{self.question[:20]}..."