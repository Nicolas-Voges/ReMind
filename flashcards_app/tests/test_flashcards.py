from django.test import TestCase
from django.contrib.auth import get_user_model
from flashcards_app.models import Flashcard, Category

User = get_user_model()

class FlashcardModelTest(TestCase):
    TEST_QUESTION = "What is TDD?"
    TEST_ANSWER = "Test-Driven Development"

    def setUp(self):
        self.test_user = User.objects.create_user(
            username="LernProfi",
            email="profi@remind.de",
            password="safePassword123"
        )
        self.cat_math = Category.objects.create(name="Mathe")
        self.cat_physics = Category.objects.create(name="Physik")

    def test_create_flashcard_with_user_defaults_and_categories(self):
        card = Flashcard.objects.create(
            user=self.test_user,
            question=self.TEST_QUESTION,
            answer=self.TEST_ANSWER
        )
        
        card.categories.add(self.cat_math, self.cat_physics)

        self.assertEqual(card.user, self.test_user)
        self.assertEqual(card.question, self.TEST_QUESTION)
        self.assertEqual(card.stage, 1)
        
        self.assertEqual(card.categories.count(), 2)
        self.assertIn(self.cat_math, card.categories.all())
        self.assertIn(self.cat_physics, card.categories.all())

        self.assertIn(card, self.cat_math.flashcards.all())