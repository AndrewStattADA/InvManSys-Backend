from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

class AuthFlowTests(APITestCase):
    def test_registration_duplicate_email_fails(self):
        User.objects.create_user(username="u1", email="test@test.com", password="p")
        data = {"username": "u2", "email": "test@test.com", "password": "p"}
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('inventory_api.views.SendGridAPIClient')
    def test_password_reset_request(self, mock_sg):
        user = User.objects.create_user(username="reset", email="reset@test.com")
        response = self.client.post('/api/password-reset/', {"email": "reset@test.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_sg.called)

    def test_password_reset_confirm_success(self):
        user = User.objects.create_user(username="reset_me", password="old")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        data = {"uid": uid, "token": token, "password": "newpassword123"}
        response = self.client.post('/api/password-reset-confirm/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        self.assertTrue(user.check_password("newpassword123"))

    def test_password_reset_invalid_uid(self):
        response = self.client.post('/api/password-reset-confirm/', {
            "uid": "gibberish-uid", "token": "token", "password": "pass"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)