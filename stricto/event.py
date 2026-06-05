"""
Module providing Event management
"""

import copy
from typing import Callable, Any
from .error import SSyntaxError


class SingletonEventManager:
    """
    Event manager object
    """

    _events_per_object = {}

    def __init__(self):
        """
        Generator
        """
        self._events_per_object = {}
        self.uniq_id = 0

    def generate_uniq_id(self) -> int:
        """Generate a uniq number for object to store events

        :return: a new number
        :rtype: int
        """
        self.uniq_id += 1
        return self.uniq_id

    def register_event(
        self, me: Any, listen_event_name: str, function: Callable
    ) -> None:
        """Register an event

        :param me: The object who listen to the event
        :type me: Any (in fact a GenericType)
        :param listen_event_name: the name of the event to listen
        :type listen_event_name: str
        :param function: the function to call when the event is trigged
        :type function: Callable
        """
        # Create events per id
        if me._event_id not in self._events_per_object:
            self._events_per_object[me._event_id] = {}

        events = self._events_per_object[me._event_id]

        if listen_event_name not in events:
            events[listen_event_name] = []
        events[listen_event_name].append(function)

    def free_events(self, me: Any) -> None:
        """Erase events for this root object

        :param me: me
        :type me: GenericType
        """
        if me._event_id in self._events_per_object:
            del self._events_per_object[me._event_id]

    def copy_object_id(self, src_id: int, dst_id: int) -> None:
        """Copy event when an object is copied

        :param src_id: _description_
        :type src_id: int
        :param dst_id: _description_
        :type dst_id: int
        """
        if src_id not in self._events_per_object:
            return

        if src_id == dst_id:
            raise SSyntaxError("Error copy _event_id event : same ids")

        if dst_id in self._events_per_object:
            raise SSyntaxError("Error copy _event_id event : already exists ")

        self._events_per_object[dst_id] = copy.copy(self._events_per_object[src_id])

    def _trigg_internal(
        self, event_name: str, root: Any, me: Any, src_object: Any, **kwargs
    ) -> None:
        """Trig reccursively the event

        :param event_name: _description_
        :type event_name: str
        :param root: _description_
        :type root: Any
        :param me: _description_
        :type me: Any
        :param src_object: _description_
        :type src_object: Any
        """

        if me._event_id in self._events_per_object:
            events = self._events_per_object[me._event_id]
            if event_name in events:
                for func in events[event_name]:
                    func(event_name, root, me, **kwargs)

        # Go deeper
        childs = me.get_childs()
        for child in childs:
            k = copy.copy(kwargs)
            self._trigg_internal(event_name, root, child, src_object, **k)

    def trigg(self, event_name: str, root: Any, src_object: Any, **kwargs) -> None:
        """Trigg an event

        :param event_name: The name of the event
        :type event_name: str
        :param root: the root object
        :type root: GenericType (usually a Dict)
        :param src_object: the object wich trigg the event
        :type src_object: GenericType
        """
        # print(f'eventmanager trigg {event_name} {type(root)}')
        self._trigg_internal(event_name, root, root, src_object, **kwargs)


EVENT_MANAGER = SingletonEventManager()
