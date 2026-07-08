from django.contrib.auth import get_user_model
from django.test import TestCase

from flashcards_app.models import Category

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
