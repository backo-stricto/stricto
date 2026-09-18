"""
Module providing to manage changes
"""

from .error import SSyntaxError


class ChangeHandler:
    """
    A class for managing changes in the object
    """

    def __init__(self):
        """ """
        self._changes = {}
        self._new_changes = {}
        self._changes_in_session = False
        self._num_of_roll = 0

    def roll(self):
        """
        move new changements _changes and restart a new set of changements
        """
        self._changes = self._new_changes
        self._new_changes = {}
        self._num_of_roll += 1

    def add(self, path_name: str):
        """
        register a changement in a sub object

        :param path_name: the path of the object who has changed
        :type path_name: str
        """
        self._changes_in_session = True
        self._new_changes[path_name] = True

        if self._num_of_roll > 10:
            raise SSyntaxError(f"{path_name} too much reccursion in compute value.")

    def __repr__(self):
        return f"ChangeHandler changes=[{ ','.join(self._changes.keys())}], new=[{ ','.join(self._new_changes.keys())}]"

    def has_change_for_me(self, path_name: str | list[str]):
        """
        return True if some change for me
        """
        if isinstance(path_name, str):
            return path_name in self._changes
        for p in path_name:
            if p in self._changes:
                return True
        return False

    def has_change(self) -> bool:
        """
        return True if some changements

        :return: if som changements
        :rtype: bool
        """
        return len(self._changes.keys()) > 0

    def has_new_change(self) -> bool:
        """
        return True if some changements

        :return: if som changements
        :rtype: bool
        """
        return len(self._new_changes.keys()) > 0

    def has_changes_in_session(self) -> bool:
        """
        return True if some changements

        :return: if som changements
        :rtype: bool
        """
        return self._changes_in_session
