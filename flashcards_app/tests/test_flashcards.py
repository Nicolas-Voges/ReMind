from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from flashcards_app.models import CardType, Category, Flashcard

from .utils import get_card_dict, get_category_dict, get_user_dict

User = get_user_model()


class ModelTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(**get_user_dict())
        self.cat_math = Category.objects.create(name="Math", user=self.test_user)
        self.cat_physics = Category.objects.create(name="Physics", user=self.test_user)

    def test_create_flashcard(self):
        default_specs = get_card_dict()
        card = Flashcard.objects.create(**get_card_dict(user=self.test_user))

        card.categories.add(self.cat_math, self.cat_physics)

        self.assertEqual(card.user, self.test_user)
        self.assertEqual(card.question, default_specs['question'])
        self.assertEqual(card.stage, 1)
        self.assertIsNotNone(card.created_at)
        self.assertIsNotNone(card.due_date)
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
        self.url = reverse('flashcard-list')
        self.credentials_creator = get_user_dict()

    def test_success(self):
        default_specs = get_card_dict()
        self.client.force_authenticate(user=self.user_creator)

        response = self.client.post(self.url, data=get_card_dict(), format='json')

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

            response = self.client.post(self.url, data=data, format='json')
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
        self.url = reverse('flashcard-detail', kwargs={'pk': self.card.pk})

    def test_success(self):
        self.client.force_authenticate(user=self.user_creator)

        response = self.client.patch(
            self.url,
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
                self.url,
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
        self.url = reverse('flashcard-detail', kwargs={'pk': self.card.pk})
        self.url_wrong = reverse('flashcard-detail', kwargs={'pk': 99999})

    def test_success(self):
        self.client.force_authenticate(user=self.user_creator)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Flashcard.objects.count(), 0)

    def test_fail(self):
        cases = [
            (
                None,
                self.url,
                status.HTTP_401_UNAUTHORIZED,
                "Anonymous user cannot delete",
            ),
            (
                self.user_creator,
                self.url_wrong,
                status.HTTP_404_NOT_FOUND,
                "A flashcard that does not exist cannot be deleted",
            ),
            (
                self.user_other,
                self.url,
                status.HTTP_404_NOT_FOUND,
                "Only creator can delete their own flashcard",
            ),
        ]

        for user, url, status_code, msg in cases:
            self.client.force_authenticate(user=user)

            response = self.client.delete(url)

            self.assertEqual(response.status_code, status_code, msg)
            self.assertEqual(Flashcard.objects.count(), 1)


class GetDetailTest(APITestCase):
    OTHER_USER_DICT = get_user_dict(**{'username': "other", 'email': "other@user.de"})

    def setUp(self):
        self.user_creator = User.objects.create_user(**get_user_dict())
        self.user_other = User.objects.create_user(**self.OTHER_USER_DICT)
        self.card = Flashcard.objects.create(**get_card_dict(user=self.user_creator))
        self.url = reverse('flashcard-detail', kwargs={'pk': self.card.pk})
        self.url_wrong = reverse('flashcard-detail', kwargs={'pk': 99999})

    def test_success(self):
        self.client.force_authenticate(user=self.user_creator)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.card.id)

    def test_fail(self):
        cases = [
            (
                None,
                self.url,
                status.HTTP_401_UNAUTHORIZED,
                "Anonymous user cannot get detail view",
            ),
            (
                self.user_creator,
                self.url_wrong,
                status.HTTP_404_NOT_FOUND,
                "Getting a non-existent card must return 404",
            ),
            (
                self.user_other,
                self.url,
                status.HTTP_404_NOT_FOUND,
                "Other user must get 404 for a foreign card due to queryset filtering",
            ),
        ]

        for user, url, status_code, msg in cases:
            self.client.force_authenticate(user=user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status_code, msg)


class GetListTest(APITestCase):
    OTHER_USER_DICT = get_user_dict(**{'username': "other", 'email': "other@user.de"})

    def setUp(self):
        self.user_creator = User.objects.create_user(**get_user_dict())
        self.user_other = User.objects.create_user(**self.OTHER_USER_DICT)
        self.url = reverse('flashcard-list') + '?size=15'

        for i in range(15):
            card_data = get_card_dict(user=self.user_creator)
            card_data['question'] = f"Question {i}"
            Flashcard.objects.create(**card_data)

    def test_success_and_pagination(self):
        cases = [
            (self.user_creator, 15, "Creator sees all 15 cards"),
            (self.user_other, 0, "Other user sees empty list"),
        ]

        for user, expected_count, msg in cases:
            self.client.force_authenticate(user=user)

            response = self.client.get(self.url)

            self.assertEqual(response.status_code, status.HTTP_200_OK, msg)

            if isinstance(response.data, dict) and 'count' in response.data:
                self.assertEqual(response.data['count'], expected_count, msg)
                self.assertEqual(
                    len(response.data['results']), min(expected_count, 15), msg
                )
            else:
                self.assertEqual(len(response.data), expected_count, msg)

    def test_fail(self):
        cases = [
            (
                None,
                status.HTTP_401_UNAUTHORIZED,
                "Anonymous user cannot get list view",
            ),
        ]

        for user, status_code, msg in cases:
            self.client.force_authenticate(user=user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status_code, msg)


class BulkPatchTest(APITestCase):
    def setUp(self):
        self.user_creator = User.objects.create(**get_user_dict())
        self.user_other = User.objects.create(
            **get_user_dict(username="other", email="other@user.com")
        )
        self.category = Category.objects.create(
            **get_category_dict(name="MyCat", user=self.user_creator)
        )
        self.category_other = Category.objects.create(
            **get_category_dict(name="OtherCat", user=self.user_other)
        )
        self.card1 = Flashcard.objects.create(
            user=self.user_creator, question="Q1", card_type="self_assessment"
        )
        self.card2 = Flashcard.objects.create(
            user=self.user_creator, question="Q2", card_type="self_assessment"
        )
        self.card_other = Flashcard.objects.create(
            user=self.user_other, question="Q3", card_type="self_assessment"
        )
        self.url = reverse('flashcard-bulk-assign-category')

    def test_success(self):
        self.client.force_authenticate(self.user_creator)

        data = {
            "category_id": self.category.pk,
            "card_ids": [self.card1.pk, self.card2.pk],
        }
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_cards = Flashcard.objects.filter(id__in=[self.card1.pk, self.card2.pk])
        for card in updated_cards:
            self.assertTrue(card.categories.filter(id=self.category.pk).exists())

    def test_fails(self):
        cases = [
            (
                None,
                {"category_id": self.category.pk, "card_ids": [self.card1.pk]},
                status.HTTP_401_UNAUTHORIZED,
                "Anonymous user cannot bulk assign categories.",
            ),
            (
                self.user_creator,
                {"category_id": "", "card_ids": []},
                status.HTTP_400_BAD_REQUEST,
                "Missing fields should return 400 Bad Request.",
            ),
            (
                self.user_creator,
                {"category_id": self.category_other.pk, "card_ids": [self.card1.pk]},
                status.HTTP_404_NOT_FOUND,
                "Using another user's category should return 404.",
            ),
            (
                self.user_creator,
                {"category_id": self.category.pk, "card_ids": [self.card_other.pk]},
                status.HTTP_400_BAD_REQUEST,
                "User should not be able to modify cards of another user.",
            ),
        ]

        for user, data, status_code, msg in cases:
            self.client.force_authenticate(user)

            response = self.client.patch(self.url, data, format='json')

            self.assertEqual(response.status_code, status_code, msg)

            card_ids = data.get("card_ids", [])
            category_id = data.get("category_id")

            if category_id and card_ids:
                actual_count = Flashcard.objects.filter(
                    id__in=card_ids, categories__id=category_id
                ).count()
                self.assertEqual(
                    actual_count, 0, f"DB Check failed: Data was modified! ({msg})"
                )
