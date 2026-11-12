# pylint: disable=duplicate-code
"""
test for selectors
"""

# pylint: disable=no-member
import unittest
from stricto import (
    Selector,
    String,
    Int,
    Dict,
    List,
    Tuple,
    STypeError,
    SAttributeError,
    SSyntaxError,
    SFilter,
    Operator,
)


class TestSelectors(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    test for Selectors
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)

        self.event_name = None

    def test_selors(self):
        """
        test selors
        """
        sel = Selector("$.name")
        self.assertEqual(repr(sel), "Selector([SI($/None/None), SI(name/None/None)])")
        self.assertEqual(repr(sel.pop()), "SI($/None/None)")
        self.assertEqual(repr(sel.pop()), "SI(name/None/None)")
        self.assertTrue(sel.empty())

        sel = Selector("$.name[0].a")
        self.assertEqual(repr(sel.pop()), "SI($/None/None)")
        self.assertEqual(repr(sel.pop()), "SI(name/None/None)")
        self.assertEqual(repr(sel.pop()), "SI(None/0/None)")
        self.assertEqual(repr(sel.pop()), "SI(a/None/None)")
        self.assertTrue(sel.empty())

        sel = Selector("$.name.")
        self.assertEqual(repr(sel.pop()), "SI($/None/None)")
        self.assertEqual(repr(sel.pop()), "SI(name/None/None)")
        self.assertEqual(repr(sel.pop()), "SI(/None/None)")
        self.assertTrue(sel.empty())

        sel = Selector("$.name[1:2]")
        self.assertEqual(repr(sel.pop()), "SI($/None/None)")
        self.assertEqual(repr(sel.pop()), "SI(name/None/None)")
        self.assertEqual(repr(sel.pop()), "SI(None/None/slice(1, 2, None))")
        self.assertTrue(sel.empty())

        sel = Selector("$.name[1][2]")
        self.assertEqual(repr(sel.pop()), "SI($/None/None)")
        self.assertEqual(repr(sel.pop()), "SI(name/None/None)")
        self.assertEqual(repr(sel.pop()), "SI(None/1/None)")
        self.assertEqual(repr(sel.pop()), "SI(None/2/None)")
        self.assertTrue(sel.empty())

    def test_selectors_equality(self):
        """
        test selectors comparison
        """
        a = Selector("$.name")
        b = Selector("$.name")
        self.assertEqual(a == "23", False)
        self.assertEqual(a == b, True)
        self.assertEqual(a == Selector("$.name.sec"), False)
        self.assertEqual(a == Selector("$.name[0]"), False)
        self.assertEqual(a == Selector("$.name[]"), False)
        self.assertEqual(a == Selector("$.name1"), False)
        self.assertEqual(a != Selector("$.name1"), True)
        self.assertEqual(a == Selector("$"), False)

    def test_selectors_gt(self):
        """
        test selectors gt
        """
        a = Selector("$.name")
        self.assertEqual(a.include(Selector("$")), False)
        self.assertEqual(Selector("$").include(a), True)
        self.assertEqual(a.include(Selector("$.b")), False)
        self.assertEqual(a.include(Selector("$.name")), True)
        self.assertEqual(a.include(Selector("$.name.b")), True)

    def test_empty_selector(self):
        """
        test empty selectors
        """
        sel = Selector(None)
        self.assertEqual(sel.empty(), True)
        sel = Selector("")
        self.assertEqual(repr(sel.pop()), "SI(/None/None)")

    def test_selector_copy(self):
        """
        test selectors
        """
        sel = Selector("$.name")
        sel2 = sel.copy()
        self.assertEqual(sel2, sel)
        sel.pop()
        self.assertNotEqual(sel2, sel)

    def test_selector_list(self):
        """
        test selector
        """
        a = List(Dict({"i": String()}))
        a.set(
            [
                {"i": "aa"},
                {"i": "bb"},
            ]
        )
        self.assertEqual(a, a)

        self.assertEqual(a.select("$[0].i"), "aa")
        se = a.select("$[0:1].i")
        self.assertEqual(se, ["aa"])
        self.assertEqual(isinstance(se, List), False)
        self.assertEqual(isinstance(a.select("$"), List), True)

        self.assertEqual(a.select("$[0:2].i"), ["aa", "bb"])
        self.assertEqual(a.select("$[].i"), ["aa", "bb"])

    def test_selector_in_dict(self):
        """
        test a complex selector in a dict
        """
        a = Dict(
            {
                "a": Int(default=1),
                "not": Int(default=1, exists=False),
                "b": Dict(
                    {
                        "l": List(Dict({"i": String()})),
                        "t": Tuple((Int(), String())),
                        "tt": Tuple((Int(), Dict({"i": String()}))),
                    }
                ),
            }
        )
        a.set(
            {
                "a": 12,
                "b": {
                    "l": [
                        {"i": "fir"},
                        {"i": "sec"},
                    ],
                    "t": (1, "top"),
                    "tt": (2, {"i": "tiptop"}),
                },
            }
        )
        self.assertEqual(a.select("$"), a)
        self.assertEqual(a.b.select("$.a"), 12)
        self.assertEqual(a.select("a"), 12)
        self.assertEqual(a.select("$.not"), None)
        self.assertEqual(a.select("@.a"), 12)
        self.assertEqual(a.select("$.a.$.a"), 12)
        self.assertEqual(a.select("$.a.@"), 12)
        self.assertEqual(a.select("$.f.d"), None)
        self.assertEqual(type(a.select("$.b.l")), List)
        self.assertEqual(a.select("$.b.l[0].i"), "fir")
        self.assertEqual(a.select("$.b.l[20].i"), None)
        self.assertEqual(a.select("$.b.l[0:2].i"), ["fir", "sec"])
        self.assertEqual(a.select("$.b.l[-1].i"), "sec")
        self.assertEqual(a.select("$.b.l[].i"), ["fir", "sec"])
        self.assertEqual(a.select("$.b.t[0]"), 1)
        self.assertEqual(a.select("$.b.t[1]"), "top")
        self.assertEqual(a.select("$.b.t[2]"), None)
        self.assertEqual(a.select("$.b.t[]"), [1, "top"])
        self.assertEqual(a.select("$.b.tt[1].i"), "tiptop")

        with self.assertRaises(SSyntaxError) as e:
            self.assertEqual(a.select("$.b.t[vla]"), None)
        self.assertEqual(e.exception.args[0], '"[vla]" is not an index or a slice')

    def test_patch(self):
        """
        test patch (RFC6902)
        """
        a = Dict(
            {
                "a": Int(default=1),
                "not": Int(default=1, exists=False),
                "b": Dict(
                    {
                        "l": List(Dict({"i": String()})),
                        "t": Tuple((Int(), String())),
                        "tt": Tuple((Int(), Dict({"i": String()}))),
                    }
                ),
            }
        )
        a.set(
            {
                "a": 12,
                "b": {
                    "l": [
                        {"i": "fir"},
                        {"i": "sec"},
                    ]
                },
            }
        )
        self.assertEqual(a, a)
        a.patch("replace", "$.a", 13)
        self.assertEqual(a.a, 13)
        with self.assertRaises(SAttributeError) as e:
            a.patch("replace", "$.notexist", 13)
        self.assertEqual(
            e.exception.to_string(), '$: Attribut does not exists "$.notexist"'
        )
        with self.assertRaises(STypeError) as e:
            a.patch("remove", "$.a")
        self.assertEqual(e.exception.to_string(), '$.a: invalid operator "remove"')
        a.patch("replace", "$.b.l[0]", {"i": "tres"})
        self.assertEqual(a.b.l[0].i, "tres")
        a.patch("replace", "$.b.l[0].i", "next")
        self.assertEqual(a.b.l[0].i, "next")
        with self.assertRaises(SAttributeError) as e:
            a.patch("replace", "$.b.l[69]", {"i": "tres"})
        self.assertEqual(
            e.exception.to_string(), '$: Attribut does not exists "$.b.l[69]"'
        )
        a.patch("add", "$.b.l", {"i": "again"})
        self.assertEqual(len(a.b.l), 3)
        self.assertEqual(a.b.l[2].i, "again")
        a.patch("remove", "$.b.l[2]")
        self.assertEqual(len(a.b.l), 2)
        a.patch("remove", "$.b.l", 1)
        self.assertEqual(len(a.b.l), 1)
        a.patch("replace", "$.b.l", [])
        self.assertEqual(len(a.b.l), 0)
        a.patch("replace", "$.b.l", [{"i": "tres"}])
        self.assertEqual(len(a.b.l), 1)

    def test_multi_selection_basic(self):
        """
        test selector
        """
        a = Int()
        a.set(12)

        ms = a.multi_select(["$"])
        self.assertEqual(ms, [12])

    def test_multi_selection_list(self):
        """
        test selector
        """
        a = List(Dict({"i": String()}))
        a.set(
            [
                {"i": "aa"},
                {"i": "bb"},
            ]
        )

        ms = a.multi_select(["$[0].i"])
        self.assertEqual(ms, ["aa"])

    def test_multi_selection(self):
        """
        test selector
        """
        a = Dict(
            {
                "a": Int(default=1),
                "not": Int(default=1, exists=False),
                "b": Dict(
                    {
                        "c": Int(default=1),
                        "l": List(Dict({"i": String()})),
                        "t": Tuple((Int(), String())),
                        "tt": Tuple((Int(), Dict({"i": String()}))),
                    }
                ),
            }
        )
        a.set(
            {
                "a": 12,
                "b": {
                    "l": [
                        {"i": "fir"},
                        {"i": "sec"},
                    ]
                },
            }
        )

        ms = a.multi_select(["$.a", "$.b.c"])
        self.assertEqual(ms, [12, 1])

    def test_filter(self):
        """test filter"""
        a = Dict(
            {
                "a": Int(default=1),
                "c": Int(default=1),
                "b": Dict(
                    {
                        "c": Int(default=1),
                        "l": List(Dict({"i": String()})),
                        "t": Tuple((Int(), String())),
                        "tt": Tuple((Int(), Dict({"i": String()}))),
                    }
                ),
            }
        )
        a.set(
            {
                "a": 12,
                "c": 22,
                "b": {
                    "c": 33,
                    "l": [
                        {"i": "fir"},
                        {"i": "sec"},
                    ],
                },
            }
        )
        f = SFilter("$.a", Operator.EQ, 12)
        self.assertEqual(repr(f), 'SFilter("$.a" Operator.EQ 12)')
        self.assertEqual(f.check(a), True)

        # Errors tests
        f = SFilter("$.a", Operator.REG, r"toto")
        self.assertEqual(f.check(a), False)
        f = SFilter("$.a", Operator.GTE, "dummy")
        self.assertEqual(f.check(a), False)
        f = SFilter("$.a", Operator.CONTAINS, SFilter("@.i", Operator.EQ, "fir"))
        self.assertEqual(f.check(a), False)

        with self.assertRaises(TypeError) as e:
            f = SFilter("$.a", Operator.CONTAINS, "aa")
        self.assertEqual(
            e.exception.args[0], "Operator Operator.CONTAINS needs a Filter"
        )
        with self.assertRaises(TypeError) as e:
            f = SFilter("$.a", Operator.NOT, "aa")
        self.assertEqual(e.exception.args[0], "Operator Operator.NOT needs a Filter")
        with self.assertRaises(TypeError) as e:
            f = SFilter("$.a", Operator.AND, "aa")
        self.assertEqual(
            e.exception.args[0], "Operator Operator.AND needs a list of Filter"
        )
        with self.assertRaises(TypeError) as e:
            f = SFilter("$.a", Operator.OR, "aa")
        self.assertEqual(
            e.exception.args[0], "Operator Operator.OR needs a list of Filter"
        )

        f = SFilter("$.b.c", Operator.GT, 22)
        self.assertEqual(repr(f), 'SFilter("$.b.c" Operator.GT 22)')
        self.assertEqual(f.check(a), True)
        f = SFilter(None, Operator.NOT, SFilter("$.a", Operator.EQ, 12))
        self.assertEqual(f.check(a), False)
        f = SFilter(
            None,
            Operator.AND,
            [SFilter("$.a", Operator.EQ, 12), SFilter("$.c", Operator.EQ, 22)],
        )
        self.assertEqual(f.check(a), True)
        self.assertEqual(
            repr(f),
            'SFilter("None" Operator.AND [SFilter("$.a" Operator.EQ 12), SFilter("$.c" Operator.EQ 22)])',
        )
        f = SFilter(
            None,
            Operator.OR,
            [SFilter("$.a", Operator.EQ, 12), SFilter("$.c", Operator.EQ, 22)],
        )
        self.assertEqual(f.check(a), True)
        f = SFilter(None, Operator.NOT, SFilter("$.a", Operator.GT, 12))
        self.assertEqual(f.check(a), True)
        f = SFilter("$.b.l", Operator.CONTAINS, SFilter("@.i", Operator.EQ, "fir"))
        self.assertEqual(f.check(a), True)
        f = SFilter("$.b.l", Operator.ALL, SFilter("@.i", Operator.EQ, "fir"))
        self.assertEqual(f.check(a), False)

    def test_auto_filter(self):
        """test filter with the simplified syntax

        No need to explicitly specify SFilter for operators that require
        filters as values.
        """
        a = Dict(
            {
                "a": Int(default=1),
                "c": Int(default=1),
                "b": Dict(
                    {
                        "c": Int(default=1),
                        "l": List(Dict({"i": String()})),
                        "t": Tuple((Int(), String())),
                        "tt": Tuple((Int(), Dict({"i": String()}))),
                    }
                ),
            }
        )
        a.set(
            {
                "a": 12,
                "c": 22,
                "b": {
                    "c": 33,
                    "l": [
                        {"i": "fir"},
                        {"i": "sec"},
                    ],
                },
            }
        )
        f = SFilter("$.a", Operator.CONTAINS, ("@.i", Operator.EQ, "fir"))
        self.assertEqual(f.check(a), False)

        with self.assertRaises(TypeError):
            # Ensures a regular TypeError is raised when an argument is missing
            f = SFilter("$.a", Operator.CONTAINS, ("@.i", Operator.EQ))

        with self.assertRaises(TypeError) as e:
            f = SFilter("$.a", Operator.CONTAINS, "aa")
        self.assertEqual(
            e.exception.args[0], "Operator Operator.CONTAINS needs a Filter"
        )
        with self.assertRaises(TypeError) as e:
            f = SFilter("$.a", Operator.NOT, "aa")
        self.assertEqual(e.exception.args[0], "Operator Operator.NOT needs a Filter")
        with self.assertRaises(TypeError) as e:
            f = SFilter("$.a", Operator.ALL, "aa")
        self.assertEqual(e.exception.args[0], "Operator Operator.ALL needs a Filter")

        with self.assertRaises(TypeError) as e:
            f = SFilter("$.a", Operator.AND, "aa")
        self.assertEqual(
            e.exception.args[0], "Operator Operator.AND needs a list of Filter"
        )

        # Ensures regular TypeError are raised if a list if provided but with
        # invalid SFilter arguments
        with self.assertRaises(TypeError) as e:
            f = SFilter("$.a", Operator.AND, ["aa"])
        with self.assertRaises(TypeError) as e:
            f = SFilter("$.a", Operator.AND, ["aa"])

        with self.assertRaises(TypeError) as e:
            f = SFilter("$.a", Operator.OR, "aa")
        self.assertEqual(
            e.exception.args[0], "Operator Operator.OR needs a list of Filter"
        )

        f = SFilter(None, Operator.NOT, ("$.a", Operator.EQ, 12))
        self.assertEqual(f.check(a), False)
        f = SFilter(
            None,
            Operator.AND,
            [("$.a", Operator.EQ, 12), ("$.c", Operator.EQ, 22)],
        )
        self.assertEqual(f.check(a), True)
        self.assertEqual(
            repr(f),
            'SFilter("None" Operator.AND [SFilter("$.a" Operator.EQ 12), SFilter("$.c" Operator.EQ 22)])',
        )
        f = SFilter(
            None,
            Operator.OR,
            [("$.a", Operator.EQ, 12), ("$.c", Operator.EQ, 22)],
        )
        self.assertEqual(f.check(a), True)
        f = SFilter(None, Operator.NOT, ("$.a", Operator.GT, 12))
        self.assertEqual(f.check(a), True)
        f = SFilter("$.b.l", Operator.CONTAINS, ("@.i", Operator.EQ, "fir"))
        self.assertEqual(f.check(a), True)
        f = SFilter("$.b.l", Operator.ALL, ("@.i", Operator.EQ, "fir"))
        self.assertEqual(f.check(a), False)
