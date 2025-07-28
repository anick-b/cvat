# Copyright (C) 2021-2022 Intel Corporation
# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

"""
Tests for cache-based account lockout functionality.
"""

from django.test import TestCase, override_settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from cvat.apps.iam.lockout_utils import (
    is_account_locked, track_failed_attempt, reset_failed_attempts,
    get_failed_attempts_count, get_lockout_remaining_time
)

User = get_user_model()


class AccountLockoutTestCase(TestCase):
    """Test cases for account lockout functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.username = "testuser"
        self.email = "testuser@example.com"
        self.password = "testpass123"

        # Clear cache before each test
        cache.clear()

        # Create a test user
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def tearDown(self):
        """Clean up after tests."""
        cache.clear()

    def test_failed_attempt_tracking(self):
        """Test that failed attempts are tracked correctly."""
        # Initially no failed attempts
        self.assertEqual(get_failed_attempts_count(self.username), 0)
        self.assertFalse(is_account_locked(self.username))

        # Simulate failed attempts
        for i in range(3):
            track_failed_attempt(self.username)
            self.assertEqual(get_failed_attempts_count(self.username), i + 1)

        # Account should be locked after 3 attempts
        self.assertTrue(is_account_locked(self.username))
        self.assertGreater(get_lockout_remaining_time(self.username), 0)

    def test_successful_login_resets_attempts(self):
        """Test that successful login resets failed attempts."""
        # Add some failed attempts
        track_failed_attempt(self.username)
        track_failed_attempt(self.username)
        self.assertEqual(get_failed_attempts_count(self.username), 2)

        # Simulate successful login
        reset_failed_attempts(self.username)

        # Failed attempts should be reset
        self.assertEqual(get_failed_attempts_count(self.username), 0)
        self.assertFalse(is_account_locked(self.username))

    def test_lockout_duration(self):
        """Test that lockout duration is applied correctly."""
        # Lock the account
        for _ in range(3):
            track_failed_attempt(self.username)

        # Check that account is locked
        self.assertTrue(is_account_locked(self.username))
        remaining_time = get_lockout_remaining_time(self.username)
        self.assertGreater(remaining_time, 0)

        # Should be locked for approximately 15 minutes (900 seconds)
        # Allow some tolerance for test timing
        self.assertGreaterEqual(remaining_time, 890)  # 15 minutes - 10 seconds tolerance

    def test_api_login_with_lockout(self):
        """Test that API login respects account lockout."""
        # Lock the account first
        for _ in range(3):
            track_failed_attempt(self.username)

        # Try to login via API
        response = self.client.post(reverse('rest_login'), {
            'username': self.username,
            'password': self.password
        })

        # Should be blocked with lockout message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Account is temporarily locked', response.content.decode())

    def test_api_login_failed_attempts(self):
        """Test that API login tracks failed attempts."""
        # Try to login with wrong password
        response = self.client.post(reverse('rest_login'), {
            'username': self.username,
            'password': 'wrongpassword'
        })

        # Should fail
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Should track failed attempt
        self.assertEqual(get_failed_attempts_count(self.username), 1)

    def test_api_login_success_resets_attempts(self):
        """Test that successful API login resets failed attempts."""
        # Add some failed attempts
        track_failed_attempt(self.username)
        track_failed_attempt(self.username)

        # Login with correct credentials
        response = self.client.post(reverse('rest_login'), {
            'username': self.username,
            'password': self.password
        })

        # Should succeed
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Failed attempts should be reset
        self.assertEqual(get_failed_attempts_count(self.username), 0)

    def test_email_based_lockout(self):
        """Test that lockout works with email as identifier."""
        # Lock account using email
        for _ in range(3):
            track_failed_attempt(self.email)

        # Should be locked
        self.assertTrue(is_account_locked(self.email))

        # Try to login with email
        response = self.client.post(reverse('rest_login'), {
            'email': self.email,
            'password': self.password
        })

        # Should be blocked
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Account is temporarily locked', response.content.decode())

    @override_settings(ENABLE_ACCOUNT_LOCKOUT=False)
    def test_lockout_disabled(self):
        """Test that lockout is disabled when setting is False."""
        # Try to lock account
        for _ in range(3):
            track_failed_attempt(self.username)

        # Should not be locked
        self.assertFalse(is_account_locked(self.username))

        # Should be able to login
        response = self.client.post(reverse('rest_login'), {
            'username': self.username,
            'password': self.password
        })

        # Should succeed
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_different_identifiers_separate_tracking(self):
        """Test that different identifiers are tracked separately."""
        # Lock account using username
        for _ in range(3):
            track_failed_attempt(self.username)

        # Should be locked
        self.assertTrue(is_account_locked(self.username))

        # Email should not be locked
        self.assertFalse(is_account_locked(self.email))

        # Login with email should work
        response = self.client.post(reverse('rest_login'), {
            'email': self.email,
            'password': self.password
        })

        # Should succeed
        self.assertEqual(response.status_code, status.HTTP_200_OK)