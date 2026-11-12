"""Module for Model (soon)"""

from copy import deepcopy
import re
from typing import Self
from .toolbox import get_content, get_class_names_hierachie


class Model:
    """
    The description of meta datas
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        t: type,
        desc: str,
        not_none: bool,
        union,
        constraints,
        default,
        transform,
        auto_set,
        exists,
        attribute_name,
        rights,
    ):
        """


        :param t: The type
        :type t: type
        :param desc: the description
        :type desc: _type_
        :param not_none: _description_
        :type not_none: _type_
        :param union: _description_
        :type union: _type_
        :param constraints: _description_
        :type constraints: _type_
        :param default: _description_
        :type default: _type_
        :param transform: _description_
        :type transform: _type_
        :param auto_set: _description_
        :type auto_set: _type_
        :param exists: _description_
        :type exists: _type_
        :param path_name: _description_
        :type path_name: _type_
        :param rights: _description_
        :type rights: _type_
        """
        self.types = get_class_names_hierachie(t)
        self.description = get_content(desc)
        self.required = get_content(not_none)
        self.union = get_content(union)
        self.constraints = get_content(constraints)
        self.default = get_content(default)
        self.transform = get_content(transform)
        self.auto_set = get_content(auto_set)
        self.exists = get_content(exists)
        self.rights = rights
        self.attribute_name = attribute_name
        self.path = ""

        self.list_model: Model = None
        self.tuple_models: list[Model] = None
        self.dict_models: dict[str, Model] = None
        self.parent: Model = None

    def __repr__(self):

        p_id = None if self.parent is None else id(self.parent)
        sub_str = ""

        if self.is_dict():
            s = []
            for _key, sub in self.dict_models.items():
                s.append(f"{sub}")
            sub_str = "\r\n".join(s)

        if self.is_list():
            sub_str = f"{self.list_model}"

        if self.is_tuple():
            s = []
            for sub in self.tuple_models:
                s.append(f"{sub}")
            sub_str = "\r\n".join(s)

        return f"M( {id(self)} {self.path_name()}({self.types[0]} parent={p_id}) {sub_str})"

    def copy(self):
        """
        Do a copy of itself
        """
        return deepcopy(self)

    def add_dict_model(self, sub: dict[str, Self]) -> None:
        """
        Add a sub model for dict

        :param sub: _description_
        :type sub: dict[str, Self]
        """
        self.dict_models = {}
        for key, model in sub.items():
            m = model
            m.attribute_name = f"{key}"
            m.path = f"{self.path}.{key}"
            m.parent = self
            self.dict_models[key] = m

    def add_list_model(self, sub_model: Self) -> None:
        """
        Add sub model for lists

        :param sub_model: _description_
        :type sub_model: Self
        """
        self.list_model = sub_model
        self.list_model.attribute_name = ""
        self.list_model.path = self.path + "."
        self.list_model.parent = self

    def path_name(self) -> str:
        """get the path name"""
        s = []
        p = self
        while p:
            s.insert(0, p.attribute_name)
            p = p.parent
        return re.sub(r"\.\[", "[", f'{".".join(s)}')

    def add_tuple_models(self, sub_models: list[Self]) -> None:
        """
        Add sub model for tuples

        :param sub_models: _description_
        :type sub_models: list[Self]
        """
        self.tuple_models = []
        index = 0
        for sub_model in sub_models:
            m = sub_model
            m.attribute_name = f"[{index}]"
            m.path = f"{self.path}[{index}]"
            m.parent = self
            self.tuple_models.append(m)
            index += 1

    def get_root(self) -> Self:
        """get the root"""
        p = self
        while p.parent:
            p = p.parent
        return p

    def is_dict(self) -> bool:
        """
        return True if this model is a dict

        :return: _description_
        :rtype: bool
        """
        if self.dict_models:
            return True
        return False

    def is_list(self) -> bool:
        """
        Return true if this model is a list

        :return: _description_
        :rtype: bool
        """
        if self.list_model:
            return True
        return False

    def is_tuple(self) -> bool:
        """
        Return true if this model is a tuple

        :return: _description_
        :rtype: bool
        """
        if self.tuple_models:
            return True
        return False

    def to_dict(self) -> dict:
        """
        Return as a dict

        :return: _description_
        :rtype: dict
        """
        a = {
            "types": self.types,
            "description": self.description,
            "required": self.required,
            "union": self.union,
            "constraints": self.constraints,
            "default": self.default,
            "transform": self.transform,
            "auto_set": self.auto_set,
            "exists": self.exists,
            "rights": self.rights,
            "attribute_name": self.attribute_name,
            "path": self.path_name(),
        }

        if self.is_dict():
            sub = {}
            for key, model in self.dict_models.items():
                sub[key] = model.to_dict()
            a["sub_scheme"] = sub

        if self.is_list():
            a["sub_type"] = self.list_model.to_dict()

        if self.is_tuple():
            sub = []
            for model in self.tuple_models:
                sub.append(model.to_dict())
            a["sub_types"] = sub

        return a
