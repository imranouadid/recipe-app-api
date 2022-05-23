from core.models import Ingredient, Recipe

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


# Test the publicity available ingredients API
class PublicIngredientApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    # Test that login is required to access endpoint
    def test_login_required(self):
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Test the private ingredients API
class PrivateIngredientApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'new_user@imran.ma',
            "this_is_password"
        )
        self.client.force_authenticate(self.user)

    # Test retrieving ingredients list
    def test_retrieve_ingredients_list(self):
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')

        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # Test that only ingredients for authenticated user are returned
    def test_ingredients_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            'other_user@imran.ma',
            'password',
        )
        Ingredient.objects.create(
            user=user2,
            name='Vinegar'
        )

        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Tuko'
        )

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    # Test create a new ingredient
    def test_create_ingredient_successful(self):
        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(user=self.user,
                                           name=payload['name']
                                           ).exists()

        self.assertTrue(exists)

    # Test creating invalid ingredients fails
    def test_create_ingredient_invalid(self):
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test filtering ingredients by those assigned to recipes
    def test_retrieve_ingredients_assigned_to_recipes(self):
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Oranges'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Banana'
        )

        recipe = Recipe.objects.create(
            user=self.user,
            title='Fruits salade',
            time_minutes=40,
            price=43
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
