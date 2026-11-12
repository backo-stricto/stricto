"""
Module providing to manage selectors
according to rfc 9535
"""

import re
from copy import deepcopy
from typing import Self
from .error import SSyntaxError


def parse_slice(s: str) -> slice | None:
    """
    parse a string and return if it is a slice

    :param s: the string
    :type s: str
    :return: a slice or None
    :rtype: slice | None
    """
    try:
        parts = s.split(":")
        if not 2 <= len(parts) <= 3:
            return None

        values = [int(x) if x else None for x in parts]
        result = slice(*values)

        if result.step == 0:
            return None

        return result
    except ValueError:
        return None


def parse_int(s: str) -> int | None:
    """
    pars a string and return if it is a int or nonte

    :param s: the string to parse
    :type s: str
    :return: the int
    :rtype: int | None
    """
    try:
        return int(s)
    except ValueError:
        return None


class SelectorItem:
    """
    A selector Item
    """

    def __init__(self, key: str = None, index: int = None, sl: slice = None):
        self.key = key
        self.index = index
        self.slice = sl

    def __repr__(self):
        return f"SI({self.key}/{self.index}/{self.slice})"

    def is_root(self) -> bool:
        """return True if match the root ($)"""
        return self.key == "$"

    def is_me(self) -> bool:
        """return True if match itself (@)"""
        return self.key == "@"

    def __eq__(self, other: Self) -> bool:
        """
        equality test of two object
        """
        if not isinstance(other, SelectorItem):
            return False

        if self.key != other.key:
            return False
        if self.index != other.index:
            return False
        if self.slice != other.slice:
            return False

        return True

    def __ne__(self, other: Self) -> bool:
        """not equal"""
        return not self.__eq__(other)


class Selector:
    """Selector
    (implementation of a description of the rfc 9535
        (https://datatracker.ietf.org/doc/rfc9535/)
    """

    def __init__(self, selector_as_string: str | None):
        """

        :param selector_as_string: a string related to rfc 9535
        :type selector_as_string: str | None
        :raises SSyntaxError: in case of non-compliant
        """
        self.selectors: list[SelectorItem] = []

        if selector_as_string is None:
            return

        s = re.sub(r"\]\[", "].[", selector_as_string)

        for sel in s.split("."):
            # selectors like blabla[...] or blabla or [...]
            match = re.search(r"(.*)\[(.*)\]", sel)
            if not match:
                self.selectors.append(SelectorItem(sel))
                continue

            if match.group(1):
                self.selectors.append(SelectorItem(match.group(1)))

            # if index is a numeric
            index = parse_int(match.group(2))
            if index is not None:
                self.selectors.append(SelectorItem(None, index))
                continue

            # if slice
            slice_attempt = parse_slice(match.group(2) if match.group(2) else ":")
            if slice_attempt:
                self.selectors.append(SelectorItem(None, None, slice_attempt))
            else:
                raise SSyntaxError('"[{0}]" is not an index or a slice', match.group(2))

    def __repr__(self):
        return f"Selector({self.selectors})"

    def empty(self):
        """
        return True if empty
        """
        if len(self.selectors) > 0:
            return False
        return True

    def copy(self):
        """
        Wrapper for copy()
        """
        return deepcopy(self)

    def pop(self):
        """
        return the first element and decrease the list of selectors
        """
        return self.selectors.pop(0)

    def __eq__(self, other: Self) -> bool:
        """
        equality test of two object
        """
        if not isinstance(other, Selector):
            return False

        if len(self.selectors) != len(other.selectors):
            return False

        # loop over selectors and go deep and check each tuple
        for i, sec in enumerate(other.selectors):
            me = self.selectors[i]
            if me != sec:
                return False

        return True

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def include(self, other: Self) -> bool:
        """if include another more restrictive Selector

        > means for Selector match more things

        example :
            $ include $.name -> True
            $.f include $.f.g -> True
            $.l include $.l[1] -> True
            $.l[1] include $.l[0].name -> False
            $.a include $.b -> False
            $.l[2] include $.l[1] -> False

            Warning :
            $.l[1:3] include $.l[1] -> False

        """
        if not isinstance(other, Selector):
            raise TypeError("include supported between instances of 'Selector'")
        # loop over selectors and go deep and check each tuple
        for i, me in enumerate(self.selectors):
            if i >= len(other.selectors):
                return False
            sec = other.selectors[i]

            if me != sec:
                return False
        return True
