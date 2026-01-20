# core/tests/conftest.py
"""Pytest configuration and fixtures for core app tests."""

# Test credentials - defined once and reused across all tests
# These are non-sensitive credentials used only in test environments
TEST_USER_PASSWORD = "TestPassword123!"  # nosec: B105 - Non-sensitive test credential
TEST_USER_USERNAME = "testuser"
TEST_USER_EMAIL = "test@example.com"
