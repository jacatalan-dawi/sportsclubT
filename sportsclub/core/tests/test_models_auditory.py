# core/tests/test_models_auditory.py
"""Unit tests for the Auditory base model."""

import time

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Address
from core.tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD, TEST_USER_USERNAME

User = get_user_model()


class AuditoryModelTest(TestCase):
    """Unit tests for the Auditory abstract model behavior."""

    def setUp(self):
        """Create a test user for auditory fields."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
        )

    def test_soft_delete(self):
        """Test soft delete functionality."""
        address = Address.objects.create(line1="Test Address")

        # Verify address exists
        self.assertEqual(Address.objects.count(), 1)

        # Soft delete
        address.soft_delete()

        # Verify it is marked as deleted
        self.assertIsNotNone(address.deleted_at)

        # Verify default manager excludes it
        self.assertEqual(Address.objects.count(), 0)

        # Verify all_objects manager includes it
        self.assertEqual(Address.all_objects.count(), 1)

    def test_restore_soft_deleted(self):
        """Test restoring a soft-deleted object."""
        address = Address.objects.create(line1="Test Address")

        # Soft delete
        address.soft_delete()
        self.assertEqual(Address.objects.count(), 0)

        # Restore
        address.restore()

        # Verify it's restored
        self.assertIsNone(address.deleted_at)
        self.assertEqual(Address.objects.count(), 1)

    def test_soft_delete_manager_filters_deleted(self):
        """Test that SoftDeleteManager properly filters deleted objects."""
        address1 = Address.objects.create(line1="Active Address")
        address2 = Address.objects.create(line1="To Delete")

        self.assertEqual(Address.objects.count(), 2)

        # Soft delete one
        address2.soft_delete()

        # Default manager should only show active
        active_addresses = Address.objects.all()
        self.assertEqual(active_addresses.count(), 1)
        self.assertEqual(active_addresses.first().id, address1.id)

    def test_all_objects_manager_includes_deleted(self):
        """Test that all_objects manager includes soft-deleted objects."""
        address1 = Address.objects.create(line1="Active Address")  # noqa: F841
        address2 = Address.objects.create(line1="Deleted Address")

        address2.soft_delete()

        # all_objects should include both
        self.assertEqual(Address.all_objects.count(), 2)

        # Can filter deleted objects
        deleted = Address.all_objects.filter(deleted_at__isnull=False)
        self.assertEqual(deleted.count(), 1)
        self.assertEqual(deleted.first().id, address2.id)

    def test_multiple_soft_deletes_updates_timestamp(self):
        """Test that calling soft_delete multiple times updates the timestamp."""
        address = Address.objects.create(line1="Test Address")

        # First soft delete
        address.soft_delete()
        first_deleted_at = address.deleted_at

        # Small delay to ensure different timestamp
        time.sleep(0.01)

        address.restore()
        address.soft_delete()
        second_deleted_at = address.deleted_at

        # Timestamps should be different
        self.assertNotEqual(first_deleted_at, second_deleted_at)
        self.assertGreater(second_deleted_at, first_deleted_at)
