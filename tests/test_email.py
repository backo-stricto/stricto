"""module for a test_email"""
import unittest
import json
from stricto import Email, SConstraintError, StrictoEncoder


class TestEmail(unittest.TestCase):
    """test unitaire for a module mail"""
    def __init__(self, m):
        unittest.TestCase.__init__(self, m)
        self.on_change_bool = False

    def test_error_constraint(self):
        """test error constraint"""
        a = Email()
        with self.assertRaises(SConstraintError) as e:
            a.set("emelie.com")
        self.assertEqual(
            e.exception.to_string(), '$:Must be a email (value="emelie.com")'
        )

    def test_json(self):
        """test a function json"""
        a = Email()
        b = Email()
        a.set("papo@pupo_toro.titi.net")
        sa = json.dumps(a, cls=StrictoEncoder)
        b.set(json.loads(sa))
        self.assertEqual(b, a)

    def test_get_value(self):
        "test value "
        a = Email()
        b = Email()
        a.set("emelie@network.fr")
        v = a.get_value()
        b.set(v)
        self.assertEqual(b, a)

    def test_get_encoded(self):
        """test encoded"""
        a = Email()
        b = Email()
        a.set("fifi.titi@toto23.too.fr")
        v = a.get_encoded()
        b.set(v)
        self.assertEqual(b, a)

    def test_default(self):
        """test value default"""
        a = Email()
        self.assertEqual(a.get_encoded(), None)
        a = Email(default="toto.tota@testpass_ok.net")
        self.assertEqual(a, "toto.tota@testpass_ok.net")
