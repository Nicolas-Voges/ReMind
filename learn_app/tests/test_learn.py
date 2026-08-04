from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.utils_test import get_card_dict, get_category_dict, get_user_dict
from flashcards_app.models import Category, Flashcard
from learn_app.models import LogReview

User = get_user_model()


class LogReviewModelTest(TestCase):
    """
    Test suite for the LogReview model in the learn application.
    Ensures correct instantiation, denormalization fields, and indexing structure.
    """

    def setUp(self):
        self.user = User.objects.create_user(**get_user_dict())
        self.category = Category.objects.create(
            **get_category_dict(user=self.user, name="Python Backend")
        )
        self.flashcard = Flashcard.objects.create(**get_card_dict(user=self.user))

    def test_log_review_creation_and_fields(self):
        """Verifies that a log entry can be created and populated correctly."""
        log = LogReview.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            category=self.category,
            was_correct=True,
            last_interval_ms=0,
        )

        self.assertEqual(log.user, self.user)
        self.assertEqual(log.flashcard, self.flashcard)
        self.assertEqual(log.category, self.category)
        self.assertTrue(log.was_correct)
        self.assertEqual(log.last_interval_ms, 0)
        self.assertLessEqual(log.created_at, timezone.now())

    def test_log_review_string_representation(self):
        """Check the __str__ method to ensure it outputs correctly in the admin panel."""
        log_correct = LogReview.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            category=self.category,
            was_correct=True,
            last_interval_ms=0,
        )

        log_incorrect = LogReview.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            category=self.category,
            was_correct=False,
            last_interval_ms=0,
        )

        today_str = str(timezone.now().date())
        self.assertIn(f"TestUser - Card {self.flashcard.id}: correct", str(log_correct))
        self.assertIn(today_str, str(log_correct))
        self.assertIn(f"TestUser - Card {self.flashcard.id}: wrong", str(log_incorrect))

    def test_meta_ordering_and_indexes(self):
        """Ensure that the meta management (sorting by creation date) is enabled."""
        log1 = LogReview.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            category=self.category,
            was_correct=True,
            last_interval_ms=0,
        )
        log2 = LogReview.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            category=self.category,
            was_correct=False,
            last_interval_ms=0,
        )

        logs = LogReview.objects.all()
        # The most recent log (log2) must be listed first using ordering = ['-created_at']
        self.assertEqual(logs[0], log2)
        self.assertEqual(logs[1], log1)
