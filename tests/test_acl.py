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
            a = ACL(List("invalid_pattern(("), False)
        self.assertEqual(
            str(e.exception), 'Invalid regex pattern: invalid_pattern'
        )
        
