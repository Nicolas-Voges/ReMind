from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

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


class PostTest(APITestCase):
    def setUp(self):
        self.user_creator = User.objects.create_user(**get_user_dict())
        self.user_other = User.objects.create_user(**get_user_dict(username="other", email="other@user.de"))
        self.create_url = reverse('flashcards-list') 
        self.credentials_creator = get_user_dict()
        self.credentials_other = get_user_dict(email=self.user_other.email)


    def test_success(self):
        default_specs = get_card_dict(user=self.user_creator)
        self.client.login(**self.credentials_creator)
        
        response = self.client.post(
            self.create_url, 
            data=get_card_dict(user=self.user_creator), 
            format="json"
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Flashcard.objects.count(), 1)
        
        new_card = Flashcard.objects.first()
        self.assertEqual(new_card.user, self.user_creator)
        self.assertEqual(new_card.question, default_specs["question"])


    def test_fail(self):
        invalid_payload = get_card_dict(user=self.user_creator)
        del invalid_payload['question']
        cases = [
            (get_card_dict(user=self.user_creator), None, status.HTTP_401_UNAUTHORIZED),
            (invalid_payload, self.user_creator, status.HTTP_400_BAD_REQUEST),
        ]

        for data, user, status_code in cases:
            if user is not None:
                self.client.login(**self.credentials_creator)
                
            response = self.client.post(
                self.create_url, 
                data=data, 
                format="json"
            )

            self.assertEqual(response.status_code, status_code)
            self.assertEqual(Flashcard.objects.count(), 0)