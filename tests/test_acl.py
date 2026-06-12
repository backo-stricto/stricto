# pylint: disable=duplicate-code, no-member
"""
test for ACL()
"""

import unittest

from stricto import ACL
from typing import List


class TestACL(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    Test on ACL
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)
        self.event_name = None

    def test_acl_init_with_invalid_pattern(self):
        """
        Test ACL initialization with invalid pattern
        """
        with self.assertRaises(ValueError) as e:
            a = ACL(r"invalid_pattern((", False)
        self.assertEqual(str(e.exception), "Invalid regex pattern: invalid_pattern((")

    def test_acl_init_with_valid_pattern(self):
        """
        Test ACL initialization with valid pattern
        """
        a = ACL(r"valid_pattern", True)
        self.assertIsInstance(a, ACL)

    def test_acl_is_a_whitelist(self):
        """
        Test ACL is_a_whitelist method
        """
        a = ACL(r"pattern", True)
        self.assertTrue(a.is_a_whitelist())
        b = ACL(r"pattern", False)
        self.assertFalse(b.is_a_whitelist())

    def test_acl_accept(self):
        """
        Test ACL accept method
        """
        a = ACL(r"^example\.com$", True)
        self.assertTrue(a.accept("example.com"))
        self.assertFalse(a.accept("test.com"))
        b = ACL(r"^example\.com$", False)
        self.assertFalse(b.accept("example.com"))
        self.assertTrue(b.accept("test.com"))

    def test_acl_is_equal(self):
        """
        Test ACL is_equal method
        """
        a = ACL(r"^example\.com$", True)
        self.assertTrue(a.is_equal(r"^example\.com$", True))
        self.assertFalse(a.is_equal(r"^example\.com$", False))
        self.assertFalse(a.is_equal(r"^test\.com$", True))

    def test_acl_str_and_repr(self):
        """
        Test ACL __str__ and __repr__ methods
        """
        a = ACL(r"^example\.com$", True)
        self.assertEqual(
            str(a), "ACL(pattern=re.compile('^example\\\\.com$'), is_whitelist=True)"
        )
        self.assertEqual(
            repr(a), "ACL(pattern=re.compile('^example\\\\.com$'), is_whitelist=True)"
        )
