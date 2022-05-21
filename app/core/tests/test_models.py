from django.test import TestCase

from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch


def sample_user(email="testo@gmail.com", password="testo"):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    # Test creating new user with an email is successful
    def test_create_user_with_email_successful(self):
        email = 'imran.ouadid@gmail.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    # Test email for new user is normalized
    def test_new_user_email_normalized(self):
        email = 'imran.ouadid@GMAIL.com'
        user = get_user_model().objects.create_user(
            email=email,
            password='testpass123'
        )

        self.assertEqual(user.email, email.lower())

    # Test creating user with no email raises error
    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '33483JD')

    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            'imran.ouadid@gmail.com',
            'testPass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    # Test the tag string representation
    def test_tag_str(self):
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan',
        )

        self.assertEqual(str(tag), tag.name)

    # Test the ingredient string representation
    def test_ingredient_str(self):
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber',
        )

        self.assertEqual(str(ingredient), ingredient.name)

    # Test the recipe string representation
    def test_recipe_str(self):
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='This is a title',
            time_minutes=4,
            price=400,
        )

        self.assertEqual(str(recipe), recipe.title)

    # Test that image is saved in the correct location
    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'my-image.jpg')

        ext_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, ext_path)
