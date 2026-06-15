# pylint: disable=duplicate-code
"""
test for event_manager
"""

import unittest
from stricto import Int


def check_pair(value, o):  # pylint: disable=unused-argument
    """
    return true if pair
    """
    return not value % 2


class TestEvent(unittest.TestCase):
    """
    Test event
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)
        self._a_event = False
        self._b_event = False

    def test_event_collision(self):
        """
        Test collision on event
        """
        self._a_event = False
        self._b_event = False

        def a_event(event_name, root, me):  # pylint: disable=unused-argument
            self._a_event = True

        def b_event(event_name, root, me):  # pylint: disable=unused-argument
            self._b_event = True

        a = Int(on=[("myevent", a_event)])
        b = Int(on=[("myevent", b_event)])

        a.trigg("myevent")
        self.assertEqual(self._a_event, True)
        self.assertEqual(self._b_event, False)
        self._a_event = False

        b.trigg("myevent")
        self.assertEqual(self._a_event, False)
        self.assertEqual(self._b_event, True)
