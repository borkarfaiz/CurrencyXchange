from django.contrib.auth import get_user_model

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

UserModel = get_user_model()


class RegistirationTest(APITestCase):
	def test_create_account(self):
		"""
		Ensure we can create a new account object.
		"""
		url = reverse("sign-up")
		data = {"username": "faiz", "password": "faiz@faiz"}
		response = self.client.post(url, data, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		data.pop("password")
		self.assertEqual(response.data, data)


class LoginTest(APITestCase):
	"""
	Ensures that user are able to login their account
	"""

	def setUp(self):
		self.user = UserModel.objects.create_user(username="borkarfaiz", password="faiz@currency")
		token, created = Token.objects.get_or_create(user=self.user)
		self.token_key = token.key
		self.url = reverse("login")

	def test_login_with_right_password(self):
		data = {"username": "borkarfaiz", "password": "faiz@currency"}
		response = self.client.post(self.url, data, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, {"token": self.token_key})

	def test_login_with_wrong_password(self):
		data = {"username": "borkarfaiz", "password": "patanahi"}
		response = self.client.post(self.url, data, format="json")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		expected_response = {"non_field_errors": ["Unable to log in with provided credentials."]}
		self.assertEqual(response.data, expected_response)

	def test_login_without_password_field(self):
		data = {"username": "borkarfaiz"}
		response = self.client.post(self.url, data, format="json")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		expected_response = {"password": ["This field is required."]}
		self.assertEqual(response.data, expected_response)