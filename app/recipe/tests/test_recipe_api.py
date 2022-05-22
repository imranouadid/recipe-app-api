import os
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


# Return URL for recipe image upload
def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    # Test creating a basic recipe
    def test_create_basic_recipe(self):
        payload = {
            "title": 'new recipe',
            "time_minutes": 3,
            "price": 34.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    # Test creating a recipe with tags
    def test_create_recipe_with_tags(self):
        tag1 = sample_tag(self.user)
        tag2 = sample_tag(self.user)

        payload = {
            "title": 'new recipe',
            "tags": [tag1.id, tag2.id],
            "time_minutes": 6,
            "price": 12.00
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    # Test creating a recipe with ingredients
    def test_create_recipe_with_ingredients(self):
        ingredient1 = sample_ingredient(self.user)
        ingredient2 = sample_ingredient(self.user)

        payload = {
            "title": 'new recipe',
            "ingredients": [ingredient1.id, ingredient2.id],
            "time_minutes": 6,
            "price": 12.00
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    # Test updating recipe with patch
    def test_partial_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user)

        payload = {'title': 'NEW TITLE', 'tags': [new_tag.id]}

        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    # Test updating a recipe with put
    def test_full_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'NEW TITLE',
            'price': 34.00,
            'time_minutes': 8,
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@imran.ma',
            'password123'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(self.user)

    def tearDown(self):
        self.recipe.image.delete()

    # Test uploading an image to recipe
    def test_upload_image_to_recipe(self):
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    # Test uploading an invalid image
    def test_upload_image_bad_request(self):
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url,
                               {
                                   'image': 'Not image, '
                                            'is just a text '
                                            '(string value)'
                               },
                               format='multipart'
                               )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
