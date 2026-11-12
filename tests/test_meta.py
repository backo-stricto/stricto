# pylint: disable=duplicate-code
"""
test for Meta informations()
"""

# pylint: disable=no-member
import unittest

from stricto import String, Int, Dict, List, Bool, Tuple, SSyntaxError, SAttributeError


class TestMeta(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    test for Meta informations()
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)

    def test_model(self):
        """
        test a Model
        """
        a = Dict(
            {
                "name": String(),
                "age": Int(default=0),
                "work": Dict(
                    {
                        "salary": Int(default=10, can_modify=False),
                        "maried": Bool(default=False),
                    },
                    exists=True,
                ),
                "nicknames": List(String()),
                "sublist": List(Dict({"a": Int()})),
                "tutu": Tuple((String(), Dict({"a": Int()}), Tuple((Int(), Bool())))),
            }
        )

        self.assertIsNone(a.get_my_model(""))
        self.assertEqual(a.get_my_model("$"), a)
        self.assertEqual(a.get_my_model("$.name"), a.name)
        self.assertEqual(a.get_my_model("$.name."), None)
        self.assertEqual(a.get_my_model("$.notexists."), None)
        self.assertEqual(a.get_my_model("$.notexists"), None)
        l = [
            ("$.name", String),
            ("$.nicknames", List),
            ("$.nicknames.", String),
            ("$.nicknames[0]", String),
            ("$.sublist[0].a", Int),
            ("$.work.salary", Int),
            ("$.tutu", Tuple),
            ("$.tutu[0]", String),
            ("$.tutu[1].a", Int),
            ("$.tutu[2][0]", Int),
        ]
        for sec in l:
            m = a.get_my_model(sec[0])
            self.assertTrue(isinstance(m, sec[1]))

    def test_simple_get_schema(self):
        """
        Test views
        """

        def is_adult(value, o):  # pylint: disable=unused-argument
            if o.age and o.age >= 18:
                return True
            return False

        def read_salary(right_name, o):  # pylint: disable=unused-argument
            if o.age and o.age >= 20:
                return True
            return False

        def modify_salary(right_name, o):  # pylint: disable=unused-argument
            if o.age and o.age >= 20:
                return True
            return False

        a = Dict(
            {
                "name": String(),
                "age": Int(default=0),
                "work": Dict(
                    {
                        "salary": Int(
                            default=10, can_read=read_salary, can_modify=modify_salary
                        ),
                        "maried": Bool(default=False),
                    },
                    exists=is_adult,
                ),
                "nicknames": List(String()),
            }
        )

        a.enable_permissions()
        a.set({"name": "toto", "age": 8, "nicknames": ["to", "toto"]})
        with self.assertRaises(SAttributeError) as e:
            self.assertNotEqual(a.work.get_schema(), None)
        self.assertEqual(
            e.exception.to_string(), '$: Dict object has no attribute "work"'
        )
        self.assertEqual(a.get_current_meta()["sub_scheme"]["work"]["exists"], False)

        a.age = 19

        with self.assertRaises(SSyntaxError) as e:
            a.work.get_current_meta()
        self.assertEqual(
            e.exception.to_string(), "$.work: get_current_meta() must start at root"
        )

        dump_main = a.get_current_meta()

        self.assertNotEqual(dump_main, None)
        self.assertEqual(
            dump_main["sub_scheme"]["work"]["sub_scheme"]["salary"]["rights"]["read"],
            False,
        )
