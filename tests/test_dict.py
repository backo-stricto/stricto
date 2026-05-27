# pylint: disable=duplicate-code, pointless-statement
"""
test for Dict()
"""

# pylint: disable=no-member
import unittest
import json

from stricto import (
    String,
    Int,
    Dict,
    List,
    Bool,
    Tuple,
    StrictoEncoder,
    STypeError,
    SConstraintError,
    SAttributeError,
    SSyntaxError,
)


class TestDict(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    test for Dict()
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)
        self.i = 0
        self.event_name = None
        self.event_trigged = False

    def test_require_only(self):
        """
        test a require only
        """
        a = Dict({"b": Int(), "c": Int(require=True)})

        with self.assertRaises(SConstraintError) as e:
            a.set({"b": 2})
        self.assertEqual(e.exception.to_string(), '$.c: Cannot be empty "None"')
        with self.assertRaises(SConstraintError) as e:
            a.set({"b": 2, "c": None})
        self.assertEqual(e.exception.to_string(), '$.c: Cannot be empty "None"')

        a.set({"b": 2, "c": 3})

    def test_simple_type(self):
        """
        Test type error
        """
        a = Dict({"b": Int(), "c": Int()})
        with self.assertRaises(STypeError) as e:
            a.set(12)
        self.assertEqual(e.exception.to_string(), '$: Must be a dict (value="12")')
        a.set({"b": 1, "c": 2})
        self.assertEqual(a.b, 1)
        self.assertEqual(a.c, 2)
        self.assertEqual(a.b + a.c, 3)
        with self.assertRaises(AttributeError) as e:
            self.assertEqual(a.d, None)
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'd'")

    def test_copy(self):
        """test copy"""
        a = Dict({"b": Int(default=3), "c": String()})
        self.assertEqual(a.b, 3)
        b = a.copy()
        self.assertEqual(b.b, 3)

        self.i = 0

        def my_default(o):  # pylint: disable=unused-argument
            self.i = self.i + 1
            return self.i

        a = Dict({"b": Int(default=my_default), "c": String()})
        self.assertEqual(a.b, 1)
        b = a.copy()
        self.assertEqual(b.b, 1)

    def test_set_error(self):
        """
        test set with error
        """
        with self.assertRaises(SSyntaxError) as e:
            Dict({"add_to_model": Int()})
        self.assertEqual(
            e.exception.to_string(),
            'Key "add_to_model" is forbidden (already used as method)',
        )
        with self.assertRaises(SSyntaxError) as e:
            Dict({"get_value": Int()})
        self.assertEqual(
            e.exception.to_string(),
            'Key "get_value" is forbidden (already used as method)',
        )

        with self.assertRaises(SSyntaxError) as e:
            Dict({"_keys": Int()})
        self.assertEqual(
            e.exception.to_string(),
            'Key "_keys" is forbidden (already used)',
        )

        with self.assertRaises(SSyntaxError) as e:
            Dict({"b": Int(), "c": Int(), "d": 23})
        self.assertEqual(
            e.exception.to_string(), 'Key "d" is not a schema "<class \'dict\'>"'
        )

        with self.assertRaises(SSyntaxError) as e:
            Dict(45)
        self.assertEqual(
            e.exception.to_string(),
            'In function "__init__", the parameter "schema" must be type <class \'dict\'>',
        )

    def test_set_none(self):
        """
        test set non existing value
        """
        a = Dict({"b": Int(), "c": Int()})
        with self.assertRaises(STypeError) as e:
            a.set(None)
        self.assertEqual(e.exception.to_string(), '$: Dict cannot be set to "None"')

    def test_set_no_value(self):
        """
        test set non existing value
        """
        a = Dict({"b": Int(), "c": Int()})
        with self.assertRaises(SAttributeError) as e:
            a.set({"b": 1, "c": 2, "d": "yolo"})
        self.assertEqual(e.exception.to_string(), '$: Dict object has no attribute "d"')

    def test_default(self):
        """
        test default values
        """
        a = Dict({"b": Int(), "c": Int()})
        self.assertEqual(a.get_value(), {"b": None, "c": None})
        a = Dict({"b": Dict({"e": Int(), "f": Int()}), "c": Int()})
        self.assertEqual(a.get_value(), {"b": {"e": None, "f": None}, "c": None})

    def test_get_encoded(self):
        """
        test default values
        """
        a = Dict({"b": Int(), "c": Int()})
        self.assertEqual(a.get_encoded(), {"b": None, "c": None})
        a = Dict({"b": Dict({"e": Int(), "f": Int()}), "c": Int()})
        self.assertEqual(a.get_encoded(), {"b": {"e": None, "f": None}, "c": None})

    def test_set_with_dict(self):
        """
        test set non existing value
        """
        a = Dict({"b": Int(), "c": Int()})
        b = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        b.check(a)
        b.set(a)
        self.assertEqual(b.b, 1)

    def test_locked(self):
        """
        test locked
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        with self.assertRaises(SAttributeError) as e:
            a.d = 22
        self.assertEqual(e.exception.to_string(), '$: Key "d" locked')

    def test_sub_undefined(self):
        """
        test locked
        """
        a = Dict({"b": Int(), "c": Int()})
        self.assertEqual(a.__dict__["_locked"], True)
        a.set({"b": 1, "c": 2})
        self.assertEqual(a.__dict__["_locked"], True)
        with self.assertRaises(AttributeError) as e:
            a.d.e = 22
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'd'")
        with self.assertRaises(SAttributeError) as e:
            a.set({"b": 1, "c": 2, "d": {"e": 1}})
        self.assertEqual(e.exception.to_string(), '$: Dict object has no attribute "d"')

    def test_sub_undefined_2(self):
        """
        test locked
        """
        a = Dict({"b": Int(), "c": Int(), "d": Dict({"e": Int()})})
        a.set({"b": 1, "c": 2})

    def test_get_keys(self):
        """
        test get keys
        """
        a = Dict({"b": Int(), "c": Int()})
        self.assertEqual(a.keys(), ["b", "c"])

    def test_len(self):
        """
        test len
        """
        a = Dict({"b": Int(), "c": Int()})
        self.assertEqual(len(a), 2)

    def test_get_item(self):
        """
        test get item
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        self.assertEqual(a["b"], 1)
        self.assertEqual(a["yolo"], None)

    def test_get(self):
        """
        test get
        """
        a = Dict({"b": Int(default=22), "c": Int()})
        a.set({"c": 2})
        self.assertEqual(a.get("b"), 22)
        self.assertEqual(a.get("c"), 2)
        self.assertEqual(a.get("notfound"), None)

    def test_am_i_root(self):
        """
        test am i root
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        self.assertEqual(a.b.am_i_root(), False)
        self.assertEqual(a.am_i_root(), True)

    def test_repr(self):
        """
        test __repr__
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        c = repr(a)
        self.assertEqual(type(c), str)
        self.assertEqual(c, "{'b': 1, 'c': 2}")

    def test_modify_schema(self):
        """
        test schema modification
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        a.add_to_model("d", String())
        a.d = "oh yeah"
        self.assertEqual(a.d, "oh yeah")
        a.remove_model("d")
        with self.assertRaises(SAttributeError) as e:
            a.d = "oh yeah"
        self.assertEqual(e.exception.to_string(), '$: Key "d" locked')

    def test_modify_schema_dict(self):
        """
        test schema modification
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})

        a.add_to_model("d", Dict({"e": String()}))
        a.d.e = "oh yeah"
        self.assertEqual(a.d.e, "oh yeah")
        self.assertEqual(a.d._parent, a)
        self.assertEqual(a.d.e._parent, a.d)
        a.remove_model("d")
        with self.assertRaises(AttributeError) as e:
            a.d.e = 22
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'd'")

    def test_equality(self):
        """
        Test equality
        """
        a = Dict({"b": Int(), "c": Int(), "not": Int(exists=False)})
        self.assertNotEqual(a, None)
        self.assertEqual(a == None, False)  # pylint: disable=singleton-comparison
        self.assertNotEqual(a, None)
        self.assertEqual(a == List(Int()), False)
        self.assertNotEqual(a, Int())
        a.set({"b": 1, "c": 2})
        b = a.copy()
        self.assertEqual(a, b)
        self.assertEqual(a == b, True)
        self.assertEqual(a != b, False)
        b.b = 22
        self.assertNotEqual(a, b)
        self.assertEqual(a == b, False)
        b = Dict({"b": Int(), "d": Int()})
        b.set({"b": 1, "d": 2})
        self.assertNotEqual(a, b)
        self.assertEqual(a != b, True)
        self.assertEqual(a == b, False)

        b = Dict({"b": Int(), "c": Int(), "not": Int(exists=True)})
        b.set({"b": 1, "c": 2})
        self.assertEqual(a != b, True)
        self.assertEqual(a == b, False)

        a = Dict({"b": Int(), "c": Int(), "d": List(Dict({"i": Int()}))})
        self.assertEqual(a, a)
        self.assertEqual(a.b.get_root(), a)
        a.set({"b": 1, "c": 2})
        self.assertEqual(a.get_root(), a)
        self.assertEqual(a, a)
        b = a.copy()
        self.assertEqual(a, b)
        self.assertEqual(b, b)
        a.c = 3
        self.assertNotEqual(a, b)
        b.c = 3
        self.assertEqual(a, b)
        b = Dict({"b": Int(), "d": List(Dict({"i": Int()}))})
        self.assertNotEqual(a, b)

    def test_copy_type(self):
        """
        Test copy
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        a.b = a.c.copy()  # pylint: disable=no-member
        a.c = 33
        self.assertEqual(a.b, 2)
        self.assertEqual(a.c, 33)

    def test_copy_permissions(self):
        """
        Test copy
        """
        a = Dict({"b": Int(), "c": Int()})
        a.disable_permissions()
        a.set({"b": 1, "c": 2})
        self.assertEqual(a.b._permissions._enabled, False)
        self.assertEqual(a.c._permissions._enabled, False)
        self.assertEqual(a._permissions._enabled, False)
        b = a.copy()
        a.enable_permissions()
        self.assertEqual(b.b._permissions._enabled, False)
        self.assertEqual(b.c._permissions._enabled, False)
        self.assertEqual(b._permissions._enabled, False)
        self.assertEqual(a.b._permissions._enabled, True)
        self.assertEqual(a.c._permissions._enabled, True)
        self.assertEqual(a._permissions._enabled, True)

    def test_copy_dict(self):
        """
        Test copy all dict
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        d = a.copy()
        self.assertEqual(type(d), type(a))
        self.assertEqual(a, d)
        a.b = 22
        self.assertNotEqual(a, d)

    def test_json(self):
        """
        Test json <-> Dict
        """
        model = {"b": Int(), "c": Int(), "e": List(String())}
        a = Dict(model)
        b = Dict(model)
        a.set({"b": 1, "c": 2, "e": ["aa", "bb"]})

        sa = json.dumps(a, cls=StrictoEncoder)
        b.set(json.loads(sa))
        self.assertEqual(b, a)

    def test_auto_set(self):
        """
        Test auto_set"""

        def my_set(o):
            return o.c + 1

        a = Dict(
            {
                "b": Int(default=12, set=my_set),
                "c": Int(default=1),
            }
        )
        self.assertEqual(a.b, 12)
        self.assertEqual(a.c, 1)
        a.set({"c": 2})
        self.assertEqual(a.b, 3)
        a.c = 33
        self.assertEqual(a.b, 34)

    def test_auto_set_2(self):
        """
        Test autoset with lambda and cascading
        """
        a = Dict(
            {
                "b": Int(default=0, set=lambda o: o.c + 1),
                "d": Int(default=0, set=lambda o: o.b + 1),
                "c": Int(default=1),
            }
        )

        self.assertEqual(a.b._parent, a)
        self.assertEqual(a.d._parent, a)

        a.set({"c": 2})
        self.assertEqual(a.b, 3)
        self.assertEqual(a.d, 4)
        a.c = 33
        self.assertEqual(a.b, 34)
        self.assertEqual(a.d, 35)

    def no_test_auto_set_reflexive(self):
        """
        reflexive in auto_set
        """
        a = Dict(
            {
                "b": Int(default=0, set=lambda o: o.d - 1),
                "d": Int(default=0, set=lambda o: o.b + 1),
                "c": Int(default=0),
            }
        )
        self.assertEqual(repr(a), "{'b': 0, 'd': 0, 'c': 0}")
        a.b = 2
        self.assertEqual(a.d, 3)
        a.d = 5
        self.assertEqual(a.b, 4)

    def no_test_auto_set_loop_stop(self):
        """
        loop in auto_set will stop
        """
        a = Dict(
            {
                "b": Int(default=0, set=lambda o: o.d + 1),
                "d": Int(default=0, set=lambda o: o.b + 1),
                "c": Int(default=0),
            }
        )
        a.set({"c": 2})
        self.assertGreater(a.b, 2)

    def test_not_exist(self):
        """
        test not exist
        """

        def check_exists(value, o):  # pylint: disable=unused-argument
            """
            return if exists or not
            """
            return o.must_exists.get_value()

        a = Dict(
            {
                "must_exists": Bool(default=False),
                "a": Int(),
                "b": Int(default=1),
                "c": Int(default=2),
                "d": Int(default=3, required=True, exists=check_exists),
                "e": Int(default=4),
            }
        )

        a.set({"d": 2})
        with self.assertRaises(SAttributeError) as e:
            a.d
        self.assertEqual(e.exception.to_string(), '$: Dict object has no attribute "d"')

        a.set({"a": 2})
        with self.assertRaises(KeyError) as e:
            print(a.get_value()["d"])
        self.assertEqual(e.exception.args[0], "d")
        with self.assertRaises(KeyError) as e:
            print(a["d"])
        self.assertEqual(e.exception.args[0], "d")
        with self.assertRaises(SAttributeError) as e:
            a.d
        self.assertEqual(e.exception.to_string(), '$: Dict object has no attribute "d"')
        self.assertEqual(a.get("d"), None)
        self.assertEqual(
            repr(a), "{'must_exists': False, 'a': 2, 'b': 1, 'c': 2, 'e': 4}"
        )

        with self.assertRaises(SAttributeError) as e:
            a.d = 2
        self.assertEqual(
            e.exception.to_string(), '$: "Dict" object has no attribute "d"'
        )

        a.set({"must_exists": False, "a": 22, "b": 11, "c": 22, "e": 44, "d": 22})

        a.must_exists = True
        self.assertEqual(a.get("d"), 22)
        self.assertEqual(a.get_value()["d"], 22)
        a.d = 2
        self.assertEqual(a.d, 2)

    def test_not_exist_parent(self):
        """
        test not exist
        """

        def check_exists(value, o):  # pylint: disable=unused-argument
            """
            return if exists or not
            """
            return o.must_exists.get_value()

        a = Dict(
            {
                "must_exists": Bool(default=False),
                "a": Int(),
                "b": Dict(
                    {
                        "e": Dict({"f": Int(default=33)}),
                        "d": Int(default=3, required=True),
                    },
                    exists=check_exists,
                ),
            }
        )
        a.set({"a": 2})
        self.assertEqual(a.get("b"), None)
        self.assertEqual(repr(a), "{'must_exists': False, 'a': 2}")

        with self.assertRaises(SAttributeError) as e:
            print(print(a.b.e["f"]))
        self.assertEqual(e.exception.to_string(), '$: Dict object has no attribute "b"')

        with self.assertRaises(SAttributeError) as e:
            a.b = {"d": 33}
        self.assertEqual(
            e.exception.to_string(), '$: "Dict" object has no attribute "b"'
        )

        with self.assertRaises(SAttributeError) as e:
            a.b.e.f = 2
        self.assertEqual(e.exception.to_string(), '$: Dict object has no attribute "b"')

        a.must_exists = True
        a.b.set({"d": 2})
        self.assertEqual(a.b.d, 2)

    def test_rollback(self):
        """
        test rollback
        """
        a = Dict(
            {
                "a": Int(),
                "b": Int(default=3, required=True),
            }
        )
        a.set({"a": 1, "b": 33})
        self.assertEqual(a.b, 33)
        self.assertEqual(a.a, 1)
        a.rollback()
        self.assertEqual(a.b, 3)
        self.assertEqual(a.a, None)
        a.set({"a": 1, "b": 33})
        with self.assertRaises(STypeError):
            a.set({"a": 11, "b": "coucou"})
        self.assertEqual(a.b, 33)
        self.assertEqual(a.a, 1)

    def test_event(self):
        """
        test for events
        """

        def trigged_load(event_name, root, me):
            self.event_name = event_name
            self.assertEqual(event_name, "load")
            self.assertEqual(root.a, 2)
            self.assertEqual(root.b, 3)
            self.assertEqual(me, a.c)

        def trigged_bb(event_name, root, me, **kwargs):
            self.event_name = event_name
            self.assertEqual(event_name, "bb")
            self.assertEqual(root.a, 2)
            self.assertEqual(root.b, 3)
            self.assertEqual(me, a.c)
            p = kwargs.pop("param_test", None)
            self.assertEqual(p, 12)

        a = Dict(
            {
                "a": Int(default=1),
                "b": Int(default=3),
                "c": Int(on=[("load", trigged_load), ("bb", trigged_bb)]),
            }
        )

        a.set({"a": 2})
        self.event_name = None
        a.trigg("load")

        self.assertEqual(self.event_name, "load")
        self.event_name = None
        a.trigg("load")
        self.assertEqual(self.event_name, "load")

        # An event with parameters
        self.event_name = None
        a.c.trigg("bb", param_test=12)
        self.assertEqual(self.event_name, "bb")

    def test_bad_event(self):
        """
        test for bad events
        """
        with self.assertRaises(TypeError) as e:
            Dict(
                {
                    "a": Int(default=1),
                    "b": Int(default=3),
                    "c": Int(on=["load", ("bb", "cc")]),
                }
            )
        self.assertEqual(
            e.exception.args[0],
            'key "on" must be list[tuple[str, typing.Callable] | tuple[str, typing.Callable, str] | tuple[str, typing.Callable, list[str]]]',
        )

    def test_path(self):
        """
        test for pathnames
        """
        a = Dict(
            {
                "a": Int(default=1),
                "b": Dict({"l": List(Dict({"i": String()}))}),
                "c": Tuple((Int(), String())),
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
                "c": (22, "h"),
            }
        )
        self.assertEqual(a.a.path_name(), "$.a")
        self.assertEqual(a.c.path_name(), "$.c")
        self.assertEqual(a.b.l.path_name(), "$.b.l")
        self.assertEqual(a.b.l[0].i.path_name(), "$.b.l[0].i")
        a.b.l.append({"i": "third"})
        self.assertEqual(a.b.l[2].i.path_name(), "$.b.l[2].i")
        with self.assertRaises(IndexError) as e:
            a.b.l[222].i.path_name()
        self.assertEqual(e.exception.args[0], "list index out of range")
        with self.assertRaises(AttributeError) as e:
            a.b.nono.i.path_name()
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'nono'")
        a.c = (22, "hop")
        self.assertEqual(a.c[0], 22)
        self.assertEqual(a.c[0].path_name(), "$.c[0]")

    def test_re_set(self):
        """
        Test re for a Dict
        """
        a = Dict(
            {
                "a": Int(default=1),
                "b": Dict({"l": List(Dict({"i": String()}))}),
                "c": Tuple((Int(), String())),
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
                "c": (22, "h"),
            }
        )
        a.set(
            {
                "a": 23,
                "b": {
                    "l": [
                        {"i": "fir"},
                        {"i": "sec"},
                        {"i": "tre"},
                    ]
                },
                "c": (23, "hh"),
            }
        )

    def test_match_equality(self):
        """
        Test dict matching equality
        """
        a = Dict(
            {
                "a": Int(default=1),
                "b": Dict({"l": List(Dict({"i": String()}))}),
                "c": Tuple((Int(), String())),
                "f": Dict({"F1": Int()}),
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
                "f": {"F1": 11},
                "c": (22, "h"),
            }
        )
        self.assertEqual(a.match({}), True)
        self.assertEqual(a.match(None), False)
        self.assertEqual(a.match({"dosnotexist": 23}), False)
        self.assertEqual(a.match({"dosnotexist": None}), False)
        self.assertEqual(a.match({"a": "12"}), False)
        self.assertEqual(a.match({"a": 12}), True)
        self.assertEqual(a.match({"a": 13}), False)
        self.assertEqual(a.match({"gg": 13}), False)
        self.assertEqual(a.match({"a": {"ff": False}}), False)
        self.assertEqual(a.match({"f": {"F1": 11}}), True)
        self.assertEqual(a.match({"f": {"F1": 12}}), False)
        self.assertEqual(a.match({"c": (22, "h")}), True)
        self.assertEqual(a.match({"c": (23, "h")}), False)

    def test_match_advance(self):
        """
        Test dict matching equality advanced
        """
        a = Dict(
            {
                "a": Int(default=1),
                "b": Dict({"l": List(Dict({"i": String()}))}),
                "c": Tuple((Int(), String())),
                "f": Dict({"F1": Int()}),
                "s": String(),
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
                "f": {"F1": 11},
                "c": (22, "h"),
                "s": "bananas",
            }
        )
        self.assertEqual(a.match({"a": ("$and", [("$gt", 11), ("$lt", 13)])}), True)
        self.assertEqual(a.match({"a": ("$or", [("$gt", 11), ("$lt", 10)])}), True)

        self.assertEqual(a.match({"a": ("$unknownoperator", 11)}), False)
        self.assertEqual(a.match({"a": ("$gt", 11)}), True)
        # With wrong type
        self.assertEqual(a.match({"a": ("$gt", "11")}), False)
        self.assertEqual(a.match({"s": ("$reg", "ban.*")}), True)
        # try a reg to a int ??
        self.assertEqual(a.match({"a": ("$reg", "ban.*")}), False)
        self.assertEqual(a.match({"s": ("$reg", "Toto.*")}), False)
        self.assertEqual(a.match({"a": ("$gt", 13)}), False)
        self.assertEqual(a.match({"a": ("$not", ("$gt", 13))}), True)
        self.assertEqual(a.match({"a": ("$reg", r"toto")}), False)
        self.assertEqual(a.match({"a": ("$not", ("$reg", r"toto"))}), True)
        self.assertEqual(a.match({"f": {"F1": ("$ne", 13)}}), True)

        self.assertEqual(a.match({"b": {"l": ("$contains", {"i": "sec"})}}), True)
        self.assertEqual(a.match({"b": {"l": ("$contains", {"i": "notfound"})}}), False)
        self.assertEqual(
            a.match({"b": {"l": ("$contains", {"i": ("$reg", r"sec")})}}), True
        )

    def test_complex_match(self):
        """
        Test dict matching with complexity
        """
        a = Int()
        a.set(12)
        self.assertEqual(a.match(12), True)
        self.assertEqual(a.match(("$and", [("$lt", 13), ("$gt", 11)])), True)
        self.assertEqual(a.match(("$and", [("$lt", 11), ("$gt", 11)])), False)
        self.assertEqual(a.match(("$or", [("$lt", 13), ("$gt", 15)])), True)

        b = Dict(
            {
                "a1": Int(),
                "a2": Int(),
            }
        )
        b.set({"a1": 10, "a2": 20})
        self.assertEqual(b.match(("$and", [{"a1": 10}, {"a2": 20}])), True)
        self.assertEqual(b.match(("$and", [{"a1": 10}, {"a2": 21}])), False)
        self.assertEqual(b.match(("$or", [{"a1": 10}, {"a2": 21}])), True)
        self.assertEqual(b.match(("$and", [{"a1": ("$gt", 9)}, {"a2": 20}])), True)
        self.assertEqual(b.match(("$and", [{"a1": ("$gt", 11)}, {"a2": 20}])), False)
        self.assertEqual(
            b.match(("$or", [{"a1": ("$gt", 11)}, {"a2": ("$lt", 22)}])), True
        )

    def test_complex_match_list(self):
        """Test match in a list"""
        a = Dict({"b": List(Int())})
        a.set({"b": [12, 13]})
        self.assertEqual(a.match({"b": ("$contains", 12)}), True)
        self.assertEqual(a.match({"b": ("$contains", 14)}), False)
        self.assertEqual(a.match({"b": ("$contains", ("$gt", 10))}), True)
        self.assertEqual(
            a.match({"b": ("$contains", ("$and", [("$gt", 10), ("$lt", 13)]))}), True
        )

    def test_dict_constraint(self):
        """check a constraint on the dict itself"""

        def must_a_be_above_b(value, o):  # pylint: disable=unused-argument
            if value["a"] > value["b"]:
                return True
            return False

        d = Dict({"a": Int(max=99), "b": Int(max=99)}, constraint=must_a_be_above_b)
        # with self.assertRaises(SConstraintError) as e:
        #     self.assertEqual(d.check({"a": 4, "b": 5}), None)
        # self.assertEqual(
        #     e.exception.to_string(),
        #     "$: Constraint not validated for value=\"{'a': 4, 'b': 5}\"",
        # )
        # self.assertEqual(d.check({"a": 6, "b": 5}), None)
        with self.assertRaises(SConstraintError) as e:
            d.set({"a": 4, "b": 5})
        self.assertEqual(
            e.exception.to_string(),
            "$: Constraint not validated for value=\"{'a': 4, 'b': 5}\"",
        )

    def test_check_value(self):
        """
        Test check value ( b > a )
        """

        def must_be_above_a(value, o):
            if o.a == None:  # pylint: disable=singleton-comparison
                return True

            if value > o.a:
                return True
            return False

        d = Dict({"a": Int(max=99), "b": Int(max=99, constraint=must_be_above_a)})

        with self.assertRaises(SConstraintError) as e:
            d.set({"a": 20, "b": 10})
        self.assertEqual(
            e.exception.to_string(), '$.b: Constraint not validated for value="10"'
        )

        self.assertEqual(d.a, None)
        self.assertEqual(d.b, None)

        with self.assertRaises(SConstraintError) as e:
            d.set({"a": 20, "b": 10})
        self.assertEqual(
            e.exception.to_string(), '$.b: Constraint not validated for value="10"'
        )
        self.assertEqual(d.a, None)
        self.assertEqual(d.b, None)

        self.assertEqual(d.check({"a": 4}), None)
        self.assertEqual(d.a.check(4), None)
        with self.assertRaises(STypeError) as e:
            d.a.check("hello")
        self.assertEqual(e.exception.to_string(), '$.a: Must be a int ("hello")')

        with self.assertRaises(SConstraintError) as e:
            d.check({"a": 100})
            d.a.check(100)
        self.assertEqual(e.exception.to_string(), '$.a: Must be below Maximal ("100")')

        # --

        # set a below b -> must rais an error
        d.set({"b": 20, "a": 10})
        self.assertEqual(d.a, 10)
        self.assertEqual(d.b, 20)
        with self.assertRaises(SConstraintError) as e:
            d.a = 22
        self.assertEqual(
            e.exception.to_string(), '$.b: Constraint not validated for value="20"'
        )

    def test_event_new(self):
        """
        Test event option
        """
        self.event_trigged = False

        def on_event(name, root, me, **kwargs):  # pylint: disable=unused-argument
            """
            just a change option
            """
            self.event_trigged = True

        a = Dict({"aa": Int(on=[("fake_event", on_event)]), "bb": Int()})
        self.assertEqual(self.event_trigged, False)
        a.set({"aa": 1, "bb": 2})
        self.assertEqual(self.event_trigged, False)
        a.trigg("fake_event")
        self.assertEqual(self.event_trigged, True)
