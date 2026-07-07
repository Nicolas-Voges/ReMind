from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from flashcards_app.models import CardType, Category, Flashcard

from .utils import get_card_dict, get_card_kwargs, get_user_dict

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
        self.create_url = reverse('flashcard-list')
        self.credentials_creator = get_user_dict()

    def test_success(self):
        default_specs = get_card_dict()
        self.client.force_authenticate(user=self.user_creator)

        response = self.client.post(
            self.create_url, data=get_card_dict(), format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flashcard.objects.count(), 1)

        new_card = Flashcard.objects.first()
        self.assertEqual(new_card.user, self.user_creator)
        self.assertEqual(new_card.question, default_specs['question'])

    def test_fail(self):
        invalid_payload = get_card_dict()
        del invalid_payload['question']
        cases = [
            (get_card_dict(), False, status.HTTP_401_UNAUTHORIZED),
            (invalid_payload, True, status.HTTP_400_BAD_REQUEST),
        ]

        for data, login, status_code in cases:
            self.client.force_authenticate(user=None)
            if login:
                self.client.force_authenticate(user=self.user_creator)

            response = self.client.post(self.create_url, data=data, format='json')
            self.assertEqual(response.status_code, status_code)
            self.assertEqual(Flashcard.objects.count(), 0)


class PatchTest(APITestCase):
    OTHER_USER_DICT = get_user_dict(**{'username': "other", 'email': "other@user.de"})
    PATCH_PAYLOAD = {
        'choices': [['text', True], ['textt', False]],
        'card_type': CardType.MULTIPLE_CHOICE.value,
    }
    PATCH_PAYLOAD_WRONG_CHOICE_VALUE = {
        'choices': [['text', True], ['textt', False], ['WRONG']],
        'card_type': CardType.MULTIPLE_CHOICE.value,
    }
    PATCH_PAYLOAD_WRONG_INCOMPATIBLE_FIELDS = {
        'answer': '',
        'card_type': CardType.TEXT_INPUT.value,
    }
    PATCH_PAYLOAD_WRONG_EMPTY_QUESTION = {'question': ""}

    def setUp(self):
        self.user_creator = User.objects.create_user(**get_user_dict())
        self.credentials_creator = get_user_dict()
        self.user_other = User.objects.create_user(**self.OTHER_USER_DICT)
        self.credentials_other = self.OTHER_USER_DICT
        self.card = Flashcard.objects.create(**get_card_dict(user=self.user_creator))
        self.patch_url = reverse('flashcard-detail', kwargs={'pk': self.card.pk})

    def test_success(self):
        self.client.force_authenticate(user=self.user_creator)

        response = self.client.patch(
            self.patch_url,
            data=self.PATCH_PAYLOAD,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.card.refresh_from_db()
        self.assertEqual(self.card.choices, self.PATCH_PAYLOAD['choices'])

    def test_fail(self):
        cases = [
            (
                None,
                self.PATCH_PAYLOAD,
                status.HTTP_401_UNAUTHORIZED,
                "Anonymous user cannot patch",
            ),
            (
                self.user_creator,
                self.PATCH_PAYLOAD_WRONG_CHOICE_VALUE,
                status.HTTP_400_BAD_REQUEST,
                "Invalid choice values must return 400",
            ),
            (
                self.user_creator,
                self.PATCH_PAYLOAD_WRONG_EMPTY_QUESTION,
                status.HTTP_400_BAD_REQUEST,
                "Empty question must return 400",
            ),
            (
                self.user_creator,
                self.PATCH_PAYLOAD_WRONG_INCOMPATIBLE_FIELDS,
                status.HTTP_400_BAD_REQUEST,
                "Incompatible fields for card type must return 400",
            ),
            (
                self.user_other,
                self.PATCH_PAYLOAD,
                status.HTTP_404_NOT_FOUND,
                "Other user gets 404 for foreign card",
            ),
        ]

        for user, payload, status_code, msg in cases:
            self.client.force_authenticate(user=user)

            response = self.client.patch(
                self.patch_url,
                payload,
                format='json',
            )

            self.assertEqual(response.status_code, status_code, msg)


class DeleteTest(APITestCase):
    OTHER_USER_DICT = get_user_dict(**{'username': "other", 'email': "other@user.de"})

    def setUp(self):
        self.user_creator = User.objects.create(**get_user_dict())
        self.user_other = User.objects.create(**self.OTHER_USER_DICT)
        self.card = Flashcard.objects.create(**get_card_dict(user=self.user_creator))
        self.delete_url = reverse('flashcard-detail', kwargs={'pk': self.card.pk})
        self.delete_url_wrong = reverse('flashcard-detail', kwargs={'pk': 99999})

    def test_success(self):
        self.client.force_authenticate(user=self.user_creator)

        response = self.client.delete(self.delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Flashcard.objects.count(), 0)

    def test_fail(self):
        cases = [
            (
                None,
                self.delete_url,
                status.HTTP_401_UNAUTHORIZED,
                "Anonymous user cannot delete",
            ),
            (
                self.user_creator,
                self.delete_url_wrong,
                status.HTTP_404_NOT_FOUND,
                "A flashcard that does not exist cannot be deleted",
            ),
            (
                self.user_other,
                self.delete_url,
                status.HTTP_404_NOT_FOUND,
                "Only creator can delete their own flashcard",
            ),
        ]

        for user, url, status_code, msg in cases:
            self.client.force_authenticate(user=user)

            response = self.client.delete(url)

            self.assertEqual(response.status_code, status_code, msg)
            self.assertEqual(Flashcard.objects.count(), 1)
