# Copyright (C) 2021-2022 Intel Corporation
# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

"""
Utility functions for cache-based account lockout functionality.
This module provides functions to track failed login attempts and manage account lockouts
using Django's cache system. Works with both LDAP and Django authentication.
"""

from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


def get_lockout_key(identifier):
    """
    Generate cache key for account lockout.

    Args:
        identifier (str): Username or email used for authentication

    Returns:
        str: Cache key for the lockout state
    """
    return f"{settings.CACHE_LOCKOUT_KEY_PREFIX}{identifier}"


def get_failed_attempts_key(identifier):
    """
    Generate cache key for failed attempts tracking.

    Args:
        identifier (str): Username or email used for authentication

    Returns:
        str: Cache key for the failed attempts count
    """
    return f"{settings.CACHE_FAILED_ATTEMPTS_KEY_PREFIX}{identifier}"


def is_account_locked(identifier):
    """
    Check if account is currently locked.

    Args:
        identifier (str): Username or email to check

    Returns:
        bool: True if account is locked, False otherwise
    """
    if not settings.ENABLE_ACCOUNT_LOCKOUT:
        return False

    lockout_key = get_lockout_key(identifier)
    locked_until = cache.get(lockout_key)

    if locked_until and timezone.now() < locked_until:
        return True
    return False


def get_lockout_remaining_time(identifier):
    """
    Get remaining lockout time in seconds.

    Args:
        identifier (str): Username or email to check

    Returns:
        int: Remaining lockout time in seconds, 0 if not locked
    """
    lockout_key = get_lockout_key(identifier)
    locked_until = cache.get(lockout_key)

    if locked_until and timezone.now() < locked_until:
        return int((locked_until - timezone.now()).total_seconds())
    return 0


def track_failed_attempt(identifier):
    """
    Track a failed login attempt and lock account if max attempts reached.

    Args:
        identifier (str): Username or email that failed authentication
    """
    if not settings.ENABLE_ACCOUNT_LOCKOUT:
        return

    failed_key = get_failed_attempts_key(identifier)
    lockout_key = get_lockout_key(identifier)

    # Increment failed attempts
    failed_attempts = cache.get(failed_key, 0) + 1
    cache.set(failed_key, failed_attempts, int(settings.RESET_FAILED_ATTEMPTS_AFTER.total_seconds()))

    # Lock account if max attempts reached
    if failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
        lockout_until = timezone.now() + settings.ACCOUNT_LOCKOUT_DURATION
        cache.set(lockout_key, lockout_until, int(settings.ACCOUNT_LOCKOUT_DURATION.total_seconds()))


def reset_failed_attempts(identifier):
    """
    Reset failed attempts on successful login.

    Args:
        identifier (str): Username or email that successfully authenticated
    """
    failed_key = get_failed_attempts_key(identifier)
    cache.delete(failed_key)


def get_failed_attempts_count(identifier):
    """
    Get current failed attempts count for an identifier.

    Args:
        identifier (str): Username or email to check

    Returns:
        int: Number of failed attempts, 0 if none
    """
    failed_key = get_failed_attempts_key(identifier)
    return cache.get(failed_key, 0)


def unlock_account(identifier):
    """
    Manually unlock an account (for admin use).

    Args:
        identifier (str): Username or email to unlock
    """
    # Remove lockout
    lockout_key = get_lockout_key(identifier)
    cache.delete(lockout_key)

    # Reset failed attempts
    failed_key = get_failed_attempts_key(identifier)
    cache.delete(failed_key)


def get_lockout_info(identifier):
    """
    Get comprehensive lockout information for an identifier.

    Args:
        identifier (str): Username or email to check

    Returns:
        dict: Dictionary containing lockout status and information
    """
    failed_attempts = get_failed_attempts_count(identifier)
    remaining_time = get_lockout_remaining_time(identifier)
    is_locked = is_account_locked(identifier)

    return {
        'identifier': identifier,
        'is_locked': is_locked,
        'failed_attempts': failed_attempts,
        'remaining_lockout_time': remaining_time,
        'max_attempts': settings.MAX_LOGIN_ATTEMPTS,
        'lockout_duration_minutes': int(settings.ACCOUNT_LOCKOUT_DURATION.total_seconds() / 60),
        'reset_after_minutes': int(settings.RESET_FAILED_ATTEMPTS_AFTER.total_seconds() / 60),
    }