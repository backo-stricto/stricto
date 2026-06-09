# pylint: disable=duplicate-code, no-member
"""
Tests for Url()
"""

import unittest
import json

from urllib.parse import urlsplit
from stricto import Url, StrictoEncoder, STypeError, SError


class TestUrl(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    Test on Url
    """

    def __init__(self, m):
        unittest.TestCase.__init__(self, m)
        self.on_change_bool = False

    def test_error_type(self):
        """
        Test error of type
        """
        a = Url()
        with self.assertRaises(STypeError) as e:
            a.set(12.3)
        self.assertEqual(
            e.exception.to_string(), '$: Must be a valid URL (value="12.3")'
        )

    # test when default is a callable that returns a valid URL
    def test_default_callable(self):
        """
        Test default value when default is a callable
        """

        def default_url(root):
            return urlsplit("http://example.com")

        a = Url(default=default_url)
        self.assertEqual(a.get_value().geturl(), "http://example.com")

    def test_default_callable_invalid(self):
        """
        Test default value when default is a callable that returns an invalid URL
        """

        def default_url(root):
            return urlsplit("not a url")

        with self.assertRaises(STypeError) as e:
            Url(default=default_url)

        self.assertEqual(e.exception.to_string(), 'Value "not a url" must be a valid URL')

    def test_default_invalid(self):
        """
        Test default value when default is invalid
        """
        with self.assertRaises(STypeError) as e:
            Url(default=123)

        self.assertEqual(e.exception.to_string(), '$: Must be a valid URL (value="123")')

    def test_default_invalid_string(self):
        """
        Test default value when default is an invalid string
        """
        with self.assertRaises(STypeError) as e:
            Url(default="not a url")
        self.assertEqual(e.exception.to_string(), '$: Must be a valid URL (value="not a url")')

    def test_string_error(self):
        """
        Test json string error
        """
        a = Url()
        with self.assertRaises(SError) as e:
            a.set("coucou")
        self.assertEqual(e.exception.to_string(), 'Value "coucou" must be a valid URL')

    def test_json(self):
        """
        Test json
        """
        a = Url()
        b = Url()
        a.set("http://example.com/path?query=1#fragment")
        json_str = json.dumps(a, cls=StrictoEncoder)
        b.set(json.loads(json_str))
        self.assertEqual(b.get_value().geturl(), a.get_value().geturl())

    def test_get_value(self):
        """
        Test get_value
        """
        a = Url()
        b = Url()
        a.set("http://example.com/path?query=1#fragment")
        v = a.get_value()
        b.set(v)
        self.assertEqual(b.get_value().geturl(), a.get_value().geturl())

    def test_get_encoded(self):
        """
        test get_encoded
        """
        a = Url()
        b = Url()
        a.set("http://example.com/path?query=1#fragment")
        v = a.get_encoded()
        b.set(v)
        self.assertEqual(b.get_value().geturl(), a.get_value().geturl())

    def test_get_encoded_in_list(self):
        """
        test get_encoded in list
        """
        a = Url()
        b = Url()
        a.set("http://example.com/path?query=1#fragment")
        v = [a.get_encoded()]
        b.set(v[0])
        self.assertEqual(b.get_value().geturl(), a.get_value().geturl())

    def test_get_encoded_when_none(self):
        """
        test get_encoded when value is None
        """
        a = Url()
        self.assertEqual(a.get_encoded(), None)

