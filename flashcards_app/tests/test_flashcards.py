from django.test import TestCase
from django.contrib.auth import get_user_model

from flashcards_app.models import Flashcard, Category
from .utils import get_user_dict, get_card_kwargs, get_card_dict

User = get_user_model()


class ModelTest(TestCase):

    def setUp(self):
        self.test_user = User.objects.create_user(**get_user_dict())
        self.cat_math = Category.objects.create(name="Math", user=self.test_user)
        self.cat_physics = Category.objects.create(name="Physics", user=self.test_user)

    def test_create_flashcard(self):
        default_specs = get_card_kwargs()
        card = Flashcard.objects.create(**get_card_dict(user=self.test_user))
        
        card.categories.add(self.cat_math, self.cat_physics)

        self.assertEqual(card.user, self.test_user)
        self.assertEqual(card.question, default_specs['question'])
        self.assertEqual(card.stage, 1)
        self.assertIsNotNone(card.created_at)
        self.assertIsNotNone(card.due_date)
        self.assertFalse(card.shared)
        self.assertEqual(card.search_terms, default_specs['search_terms'])
        self.assertEqual(card.choices, default_specs['choices'])
        self.assertEqual(card.notes, default_specs['notes'])
        self.assertEqual(card.categories.count(), 2)
        self.assertIn(self.cat_math, card.categories.all())
        self.assertIn(self.cat_physics, card.categories.all())

        self.assertIn(card, self.cat_math.flashcards.all())


