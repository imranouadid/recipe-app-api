from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


# Return recipe detail URL
def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


# Create and return a simple tag object
def sample_tag(user, name="Main course"):
    return Tag.objects.create(user=user, name=name)


# Create and return a simple ingredient object
def sample_ingredient(user, name="Cinnamon"):
    return Ingredient.objects.create(user=user, name=name)


# Create and return a simple recipe
def sample_recipe(user, **params):
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 5,
        'price': 10.00
    }

    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


# Test unauthenticated recipe API test
class PublicRecipeApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    # Test that authenticated is required
    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Test authenticated recipe API access
class PrivateRecipeApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@imran.ma',
            'passwordfor@me'
        )

        self.client.force_authenticate(self.user)

    # Test retrieving a list of recipes
    def test_retrieve_recipes(self):
        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # # Test retrieving recipes of user
    def test_recipes_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            'other_user@imran.ma',
            'passwor1234@'
        )

        sample_recipe(self.user)
        sample_recipe(user2)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(
            user=self.user
        )
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    # Test viewing a recipe detail
    def test_view_recipe_detail(self):
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredient(self.user))

        url = detail_url(recipe.id)

        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)
