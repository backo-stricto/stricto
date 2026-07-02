"""Module providing the List() Class"""

import copy
import json
from typing import Any, Self
from .generic import GenericType, ViewType
from .error import SError, SAttributeError
from .toolbox import get_content


class ListAndTuple(GenericType):  # pylint: disable=too-many-instance-attributes
    """
    A Mutualisation for List and Tuples
    """

    def __init__(self, **kwargs):
        """
        initialisation, set class_type and some parameters
        """

        GenericType.__init__(self, **kwargs)

    def __copy__(self):
        result = GenericType.__copy__(self)
        # result.__dict__.update(self.__dict__)
        result._value = None
        v = GenericType.get_value(self)
        if isinstance(v, list):
            result._value = []
            for i in v:
                result._value.append(copy.copy(i))
        return result

    def enable_permissions(self):
        """
        set permissions to on
        """
        GenericType.enable_permissions(self)
        v = GenericType.get_value(self)
        if isinstance(v, list):
            for i in v:
                i.enable_permissions()

    def disable_permissions(self):
        """
        set permissions to off
        """
        GenericType.disable_permissions(self)
        v = GenericType.get_value(self)
        if isinstance(v, list):
            for i in v:
                i.disable_permissions()

    def get_current_meta(self, parent: dict = None):
        """
        Return a schema for this object
        """
        a = GenericType.get_current_meta(self, parent)
        a["min"] = get_content(self._min)
        a["max"] = get_content(self._max)
        a["uniq"] = get_content(self._uniq)

        return a

    def __json_encode__(self):
        """
        Called by the specific Encoder
        """
        v = GenericType.get_value(self)
        if v is None:
            return None
        a = []
        for i in v:
            if i.exists_or_can_read() is False:
                continue
            a.append(i.get_encoded())
        return a

    def get_view(self, view_name, final=True):  # pylint: disable=protected-access
        """
        Return all elements belonging to view_name
        tue return is a subset of this Dict
        """
        my_view = self._belongs_to_view(view_name)

        if my_view is ViewType.NO:
            return (ViewType.NO, None) if final is False else None

        if my_view is ViewType.YES:
            return (ViewType.YES, self.copy()) if final is False else self.copy()

        v = GenericType.get_value(self)

        if v is None:
            return (ViewType.NO, None) if final is False else None

        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result._value = []  # pylint: disable=protected-access
        for i in v:
            if i.exists_or_can_read() is False:
                continue
            s = i.get_view(view_name, False)
            if s[0] is ViewType.YES:
                result._value.append(s[1])  # pylint: disable=protected-access
                continue
            if s[0] is ViewType.NO:
                continue
        # if my_view is ViewType.EXPLICIT_UNKNOWN:
        #     if len(result) == 0:
        #         return (ViewType.NO, None) if final is False else None
        # if my_view is ViewType.UNKNOWN:
        #     if len(result) == 0:
        #        return (ViewType.NO, None) if final is False else None
        return (ViewType.YES, result) if final is False else result

    def get_childs(self) -> list[Self]:

        if self._value is None:
            return []

        a = []
        for v in self._value:
            if v.exists_or_can_read() is False:
                continue
            a.append(v)
        return a

    def start_record(self) -> None:
        """
        Record the value in case of Rollback
        overwrite GenericType.start_record
        """

        # self._old_value = self._value
        if self._value is None:
            self._old_value = None
            return

        self._old_value = []
        for v in self._value:
            if v is None:
                self._old_value.append(v)
                continue
            v.start_record()
            self._old_value.append(v.copy())

    def end_record(self) -> bool:
        """
        The process of update is OK
        :return: True if changed
        :rtype: bool
        """
        self._updating_process = False
        if self._value is None:
            return False
        changed = False
        for v in self._value:
            if v is None:
                continue
            c = v.end_record()
            if c is True:
                changed = True
        return changed

    def rollback(self) -> None:
        """
        reset to the old value
        """
        self._updating_process = False
        self._value = self._old_value

        if self._value is None:
            return

        for v in self._value:
            if v is None:
                continue
            v.rollback()

    def check_value(self) -> None:
        """
        Check of the value is compliant to contraints
        or throw an error
        """

        # Cannot read
        if self.exists_or_can_read() is False:
            raise SAttributeError("{0}: Locked", self.path_name())

        if self._value is not None:
            self.check_type(self._value)

        if isinstance(self._value, list):
            for v in self._value:
                if v.exists_or_can_read() is not False:
                    v.check_value()

        # Check constraints
        self.check_constraints(self.get_value())

    def set_default_value(self) -> bool:
        """Set the default value

        from the default= function or direct value

        :return: True if changed
        :rtype: bool
        """
        changed = False

        if self._value is not None:
            return False

        # There is a default for this List or Tuple.
        if self._default is not None:

            default_value = None
            if not callable(self._default):
                default_value = self._default
            else:
                default_value = self._default(self.get_root())

            # Check correct type or raise an Error
            if default_value is not None:
                self.check_type(default_value)

                self._value = []
                index = 0
                for val in default_value:
                    v = self._set_element_value(  # pylint: disable=assignment-from-none
                        val, index
                    )
                    self._value.append(v)
                    index = index + 1
                    changed = True

        # Set childs defaults
        if self._value is not None:
            for v in self._value:
                if v is None:
                    continue
                c = v.set_default_value()
                if c is True:
                    changed = True
        return changed

    def compute_value(self) -> bool:
        """compute the value if needed

        :return: True if changed
        :rtype: bool
        """
        changed = False

        if callable(self._auto_set):
            value = self._auto_set(self.get_root())

            if value is not None:
                self.check_type(value)

                self._value = []
                index = 0
                for val in value:
                    v = self._set_element_value(  # pylint: disable=assignment-from-none
                        val, index
                    )
                    self._value.append(v)
                    index = index + 1
                    changed = True

        # compute defaults for childs
        if self._value is not None:
            for v in self._value:
                if v is None:
                    continue
                c = v.compute_value()
                if c is True:
                    changed = True
        return changed

    def _set_element_value(  # pylint: disable=unused-argument
        self, value: Any, index: int = 0
    ) -> GenericType:
        """
        Set an element From model

        must be overwritten
        """
        return None

    def __json_decode__(self, value):
        """
        Called by the specific Decoder
        """
        return json.loads(value)

    def set_value(self, value: Any) -> bool:
        """Set hardly the value

        1. do the transform function
        2. check the type
        3. set the value

        :return: True if has changed
        :rtype: bool
        """

        corrected_value = value.get_value() if isinstance(value, GenericType) else value

        if callable(self._transform):
            corrected_value = self._transform(corrected_value, self.get_root())

        if isinstance(corrected_value, str):
            try:
                corrected_value = self.__json_decode__(corrected_value)
            except Exception as e:  # pylint: disable=broad-exception-caught
                raise SError(e, self.path_name(), json=corrected_value) from e

        # Check correct type or raise an Error
        if corrected_value is not None:
            self.check_type(corrected_value)

        changed = False
        self._value = []
        index = 0
        if corrected_value is not None:
            for val in corrected_value:
                v = self._set_element_value(  # pylint: disable=assignment-from-none
                    val, index
                )
                self._value.append(v)
                index = index + 1
                changed = True

        return changed
