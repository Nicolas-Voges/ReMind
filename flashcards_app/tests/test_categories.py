from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from flashcards_app.models import Category

from .utils import get_category_dict, get_user_dict

User = get_user_model()


class ModelTest(TestCase):
    TEST_NAME = "Geometry"

    def setUp(self):
        self.test_user = User.objects.create_user(
            username="LernProfi", email="profi@remind.de", password="safePassword123"
        )
        self.cat_math = Category.objects.create(name="Math", user=self.test_user)

    def test_create_category(self):
        category = Category.objects.create(
            user=self.test_user, name=self.TEST_NAME, parent=self.cat_math
        )

        self.assertEqual(category.user, self.test_user)
        self.assertEqual(category.name, self.TEST_NAME)
        self.assertEqual(str(category), self.TEST_NAME)
        self.assertEqual(category.parent, self.cat_math)


class PostTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(**get_user_dict())
        self.url = reverse('category-list')

    def test_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, get_category_dict(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.user.pk)
        self.assertEqual(response.data['parent'], None)
        self.assertEqual(Category.objects.count(), 1)

    def test_fails(self):
        cases = [
            (
                None,
                get_category_dict(),
                status.HTTP_401_UNAUTHORIZED,
                "Unauthorized user cannot post a category.",
            ),
            (
                self.user,
                get_category_dict(name=""),
                status.HTTP_400_BAD_REQUEST,
                "Category name cannot be empty.",
            ),
        ]

        for user, data, status_code, msg in cases:
            self.client.force_authenticate(user=user)

            response = self.client.post(self.url, data, format='json')

            self.assertEqual(response.status_code, status_code, msg)
            self.assertEqual(Category.objects.count(), 0)


class PatchTest(APITestCase):
    def setUp(self):
        self.user_creator = User.objects.create(**get_user_dict())
        self.user_other = User.objects.create(
            **get_user_dict(username="other", email="other@user.com")
        )
        self.category = Category.objects.create(
            **get_category_dict(user=self.user_creator)
        )
        self.category_parent = Category.objects.create(
            **get_category_dict(name="ParentCat", user=self.user_creator)
        )
        self.category_other_user = Category.objects.create(
            **get_category_dict(user=self.user_other, name='OtherUsersCategory')
        )
        self.url = reverse('category-detail', kwargs={'pk': self.category.pk})

    def test_success(self):
        self.client.force_authenticate(self.user_creator)

        response = self.client.patch(
            self.url, get_category_dict(parent=self.category_parent.pk, format='json')
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Category.objects.count(), 3)

    def test_fails(self):
        cases = [
            (
                None,
                {'parent': self.category_parent.pk},
                status.HTTP_401_UNAUTHORIZED,
                "An annonymous user cannot edit a category! A 401 error should be returned.",
            ),
            (
                self.user_creator,
                {'parent': self.category.pk},
                status.HTTP_400_BAD_REQUEST,
                "A Category cannot be its own parent. A 400 error should be returned.",
            ),
            (
                self.user_other,
                {'name': "Not mine"},
                status.HTTP_404_NOT_FOUND,
                "A Category cannot be its own parent. A 404 error should be returned.",
            ),
        ]

        for user, data, status_code, msg in cases:
            self.client.force_authenticate(user)

            response = self.client.patch(self.url, data, format='json')

            self.assertEqual(response.status_code, status_code, msg)
