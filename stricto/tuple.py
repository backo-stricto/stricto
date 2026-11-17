"""Module providing the Tuple() Class"""

import copy
from typing import Any, Self
from .generic import GenericType
from .list import List
from .list_and_tuple import ListAndTuple
from .error import STypeError, SSyntaxError
from .selector import Selector
from .toolbox import validation_parameters


class Tuple(ListAndTuple):
    """
    A Tuple Type
    """

    @validation_parameters
    def __init__(self, schema: tuple, **kwargs):
        """ """

        ListAndTuple.__init__(self, **kwargs)

        self._json_path_separator = ""

        self._schema = []
        i = 0
        for element_schema in schema:
            if isinstance(element_schema, GenericType) is False:
                raise SSyntaxError('Not a schema ("{schema}")', schema=element_schema)
            mm = copy.copy(element_schema)
            mm._parent = self

            mm._attribute_name = f"[{i}]"
            self._schema.append(mm)
            i = i + 1

        self._locked = True

    def __copy__(self):
        result = GenericType.__copy__(self)
        result._schema = []
        i = 0
        for s in self._schema:
            new_sub = copy.copy(s)
            new_sub._attribute_name = f"[{i}]"
            new_sub._parent = self
            result._schema.append(new_sub)
            i = i + 1
        return result

    def _set_element_value(self, value: Any, index: int = 0) -> GenericType:
        """Set an element From model"""
        if index >= len(self._schema):
            raise STypeError("{0}: Tuple schema to short", self.path_name())

        my_type = self._schema[index]
        m = my_type.copy()
        m._attribute_name = f"[{index}]"
        m._parent = self
        m.set_value(value)
        return m

    def get_schema(self):
        """Return meta information for a float

        :param self: Description
        :return: :func:`GenericType.get_schema`

        :rtype: dict

        :meta private:
        """
        a = GenericType.get_schema(self)
        a["sub_types"] = []
        for schema in self._schema:
            a["sub_types"].append(schema.get_schema())
        return a

    def get_current_meta(self, parent: dict = None):
        """
        Return a schema for this object
        """
        a = ListAndTuple.get_current_meta(self, parent)

        a["sub_types"] = []

        v = GenericType.get_value(self)
        for i in v:
            a["sub_types"].append(i.get_current_meta(a))
        return a

    def get_my_model_by_selector(self, sel: Selector) -> Self:

        if sel is None:
            return None

        # The end of the chain
        if sel.empty():
            return self

        # go further
        sel_item = sel.pop()
        if sel_item.is_root():
            return self.get_root().get_my_model_by_selector(sel)
        if sel_item.is_me():
            return self.get_my_model_by_selector(sel)

        if sel_item.key is not None:
            return None
        if sel_item.slice is not None:
            return None
        if sel_item.index is None:
            return None

        sub_model = None
        try:
            sub_model = self._schema[sel_item.index]
        except IndexError:
            return None

        return sub_model.get_my_model_by_selector(sel)

    def get_value(self):
        """
        get the value
        """
        v = GenericType.get_value(self)
        if v is None:
            return None

        a = []
        for sub_value in v:
            a.append(sub_value.get_value())
        return tuple(a)

    def get_encoded(self) -> list:
        """Return the encoded value

        :return: the value as a encoded for json
        :rtype: list
        """
        v = GenericType.get_value(self)
        if v is None:
            return None

        a = []
        for sub_value in v:
            a.append(sub_value.get_encoded())
        return tuple(a)

    def __repr__(self):
        a = []
        v = GenericType.get_value(self)
        if v is None:
            return "None"

        for sub_value in v:
            a.append(sub_value)
        return tuple(a).__repr__()

    def __len__(self):
        """
        calld by len()
        """
        return len(self._schema)

    def __eq__(self, other):
        """
        equality test tuple
        """
        list_of_content = self.get_value()

        o_list = None
        if isinstance(other, Tuple):
            o_list = other.get_value()
        elif isinstance(other, tuple):
            o_list = other

        if list_of_content is None:
            return o_list is None

        if not isinstance(o_list, tuple):
            return False

        if len(list_of_content) != len(o_list):
            return False
        for index, v in enumerate(list_of_content):
            o = o_list[index]
            if v != o:
                return False
        return True

    def match(self, other):
        """
        Check if equality with an object
        """
        v = GenericType.get_value(self)
        if other is None:
            return v is None

        if isinstance(other, tuple) is False:
            return False

        return tuple(v) == other

    def __ne__(self, other):
        """
        equality test two objects
        """
        return not self.__eq__(other)

    def __lt__(self, other):
        """
        lt test two objects
        """
        v = GenericType.get_value(self)
        t = None if v is None else tuple(v)
        return t < self._get_other_value(other)

    def __le__(self, other):
        """
        le test two objects
        """
        v = GenericType.get_value(self)
        t = None if v is None else tuple(v)
        return t <= self._get_other_value(other)

    def __gt__(self, other):
        """
        gt test two objects
        """
        v = GenericType.get_value(self)
        t = None if v is None else tuple(v)
        return t > self._get_other_value(other)

    def __ge__(self, other):
        """
        ge test two objects
        """
        v = GenericType.get_value(self)
        t = None if v is None else tuple(v)
        return t >= self._get_other_value(other)

    def __add__(self, other):
        """
        add two Tuples
        """
        return self.get_value() + self._get_other_value(other)

    def __getitem__(self, index):
        v = GenericType.get_value(self)
        if v is None:
            return None
        return v[index]

    def check_type(self, value):
        """
        check if conplain to model or raise an
        """
        if isinstance(value, (tuple, Tuple, list, List)):
            return True

        raise STypeError(
            '{0}: Must be a tuple or a Tuple (value="{value})',
            self.path_name(),
            value=value,
        )

    def check_constraints(self, value):
        GenericType.check_constraints(self, value)
        return True
