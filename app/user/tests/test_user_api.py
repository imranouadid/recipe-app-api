from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    get_user_model().objects.create_user(**params)


# Test the users API (public)
class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    # Test creating user with valid payload is successful
    def test_create_valid_user_success(self):
        payload = {
            'email': 'test123@gmail.com',
            'password': 'testpass',
            'name': 'Test Name',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        # self.assertEqual(user.email, payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    # Test creating user that already exists fails
    def test_user_exists(self):
        payload = {
            'email': 'test123@gmail.com',
            'password': 'testpass',
            'name': 'Test Name',
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test that the password must be more than 5 characters
    def test_password_too_short(self):
        payload = {
            'email': 'test123@gmail.com',
            # Short password less than 5
            'password': 'im',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        is_user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(is_user_exists)

    # Test that a token is created for the user
    def test_create_token_for_user(self):
        payload = {
            'email': 'test123@gmail.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # Test that token is not created when if invalid credentials are given
    def test_create_token_invalid_credentials(self):

        create_user(email="testmail@imran.ma", password='testapass123')
        payload = {
            'email': "testmail@imran.ma",
            'password': 'wrong_pass',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        payload = {
            'email': 'testmail@imran.ma',
            'password': 'testmail',
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test that email and password are required
    def test_creating_user_missing_fields(self):
        res = self.client.post(TOKEN_URL,
                               {
                                   'email': 'incorrect mail',
                                   'password': ''
                                }
                               )
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
