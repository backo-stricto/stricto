import unittest
from stricto import ACLS, ACL


class TestACLS(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    """*test if ACL is a whitelist et result equal true so accept a domain """

    def test_authorize_is_a_whitelist_and_default_is_false(self):
        l = ACLS(
            [
                ACL("toto.titi@mail.com", True),
                ACL("fifi.com", True),
                ACL("fofo.org", True),
            ],
            default=False,
        )

        self.assertTrue(l.authorize("fifi.com"))

    """*test if ACL do not a whitelist et result equal false so do not accept a domain """

    def test_authorize_is_a_not_whitelist_and_default_true(self):
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
