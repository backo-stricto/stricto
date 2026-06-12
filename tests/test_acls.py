"test module acls"
import unittest
from stricto import ACLS, ACL

class TestACLS(unittest.TestCase):
    """class of test ACLS"""
    def __init__(self, *args, **kwargs):
        "init test ACLs"
        super().__init__(*args, **kwargs)

    def test_authorize_is_a_whitelist_and_default_is_false(self):
        """*test if ACL is a whitelist et result equal true so accept a domain """

        l = ACLS(
            [
                ACL("toto.titi@mail.com", True),
                ACL("fifi.com", True),
                ACL("fofo.org", True),
            ],
            default=False,
        )

        self.assertTrue(l.authorize("fifi.com"))
    def test_authorize_is_a_not_whitelist_and_default_true(self):
        """list ACLS that return False """
        l = ACLS(
            [
                ACL("example.fr", False),
                ACL("coctiti.com", False),
                ACL("fifi.org", False),
            ],
            default=True,
        )

        self.assertFalse(l.authorize("fifi.org"))

    def test_authorize_is_whitelist_and_is_not_whitelist_not_accept(self):
        """list ACLS who authorize if acls is not whitelist and not accept"""
        l = ACLS(
            [
                ACL("tootio.titi.fr", True),
                ACL("caprice@gmail.org", False),
                ACL("titi.fr", False),
                ACL(r".*\.captivee.com", True),
                ACL("captivif.fr", True),
            ],
            default=False,
        )
        self.assertFalse(l.authorize("titi.fr"))
    def test_authorize_is_whitelist_ant_is_not_whitlist_is_accept(self):
        """list acls who authorize if donmain is accept and not whitelist"""

        l = ACLS(
            [
                ACL("tootio.titi.fr", True),
                ACL("caprice@gmail.org", False),
                ACL("titifine.fr", True),
                ACL(r".*\.captivee.com", True),
                ACL("titifine.fr", True),
            ],
            default=False,
        )
        self.assertTrue(l.authorize("titifine.fr"))
    def test_not_math_and_is_whitelist(self):
        """not math"""

        l = ACLS(
            [
                ACL("coctiti.com", False),
                ACL("foutooo.org", True),
                ACL("pipooo.org", False),
                ACL("tooo.org", True),
            ],
            default=True,
        )
        self.assertTrue(l.authorize("foutooou.org"))
    def test_math_and_is_not_whitelist(self):
        """match and is not whitelist"""

        l = ACLS(
            [
                ACL("toiti.fr", True),
                ACL("gogo.com", False),
                ACL("nanotooi.fr", True),
                ACL("gogo.com", True),
            ],
            default=True,
        )
        self.assertFalse(l.authorize("gogo.com"))
    def test_not_math_and_is_not_whitelist(self):
        """ notch and not whitelist"""

        l = ACLS(
            [
                ACL("toiti.fr", True),
                ACL("gogo.com", False),
                ACL("nanotooi.fr", True),
                ACL("gogo.com", True),
            ],
            default=False,
        )
        self.assertFalse(l.authorize("gogoco.com"))
