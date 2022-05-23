from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


# Test the publicly available tags API
class PublicTagsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    # Test that login is required for retrieving tags
    def test_login_required(self):

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Test the authorized user tags API
class PrivateTagsApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@imran.ma',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # Test retrieving tags
    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # Test that tags returned are for the authenticated user
    def test_tags_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            'other@imran.ma',
            'testpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    # Test creating a new tag
    def test_create_tag_successful(self):
        payload = {"name": "new test tag"}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    # Test creating a new tag with invalid payload
    def test_create_invalid_tag(self):
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test filtering tags by those assigned to recipes
    def test_retrieve_tags_assigned_to_recipes(self):
        tag1 = Tag.objects.create(
            user=self.user,
            name='Breakfast'
        )
        tag2 = Tag.objects.create(
            user=self.user,
            name='Lunch'
        )

        recipe = Recipe.objects.create(
            user=self.user,
            title='Coriander Eggs',
            time_minutes=40,
            price=43
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
