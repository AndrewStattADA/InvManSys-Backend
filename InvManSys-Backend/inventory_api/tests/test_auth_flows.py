from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

# --- AUTHENTICATION FLOW TEST SUITE ---
# Verifies critical security and user account operations
class AuthFlowTests(APITestCase):
    
    def test_registration_duplicate_email_fails(self):
        """Verify that the API prevents two users from using the same email."""
        # Pre-create a user with a specific email
        User.objects.create_user(username="u1", email="test@test.com", password="p")
        
        # Attempt to register a second user with that same email
        data = {"username": "u2", "email": "test@test.com", "password": "p"}
        response = self.client.post('/api/register/', data)
        
        # Assert that the request fails with a 400 error (validation error)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('inventory_api.views.SendGridAPIClient')
    def test_password_reset_request(self, mock_sg):
        """Ensure requesting a reset triggers an email via SendGrid."""
        # Create a user to request a reset for
        user = User.objects.create_user(username="reset", email="reset@test.com")
        
        # Perform the request; @patch mocks the actual SendGrid call to prevent sending real emails
        response = self.client.post('/api/password-reset/', {"email": "reset@test.com"})
        
        # Assert the API responded correctly and the mailing service was contacted
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_sg.called)

    def test_password_reset_confirm_success(self):
        """Verify the full flow: generating a valid token and updating the password."""
        # Setup: Create a user and manually generate their reset UID and Token
        user = User.objects.create_user(username="reset_me", password="old")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # Submit the new password using the generated credentials
        data = {"uid": uid, "token": token, "password": "newpassword123"}
        response = self.client.post('/api/password-reset-confirm/', data)
        
        # Check for success response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh user object from the database and verify the password has actually changed
        user.refresh_from_db()
        self.assertTrue(user.check_password("newpassword123"))

    def test_password_reset_invalid_uid(self):
        """Ensure the API rejects malformed or invalid UIDs during password reset."""
        # Attempt to submit a reset with a non-base64 or incorrect UID
        response = self.client.post('/api/password-reset-confirm/', {
            "uid": "gibberish-uid", "token": "token", "password": "pass"
        })
        
        # Assert that the system catches the error and returns a 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)