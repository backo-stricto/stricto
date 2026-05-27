"""
Module providing Event management
"""

import copy
from typing import Callable, Any
from .selector import Selector
from .toolbox import validation_parameters


class StrictoEvent:
    """Stricto Event"""

    listen_selectors: list[Selector] = None
    listen_event_name: str = None
    function: Callable = None
    me: Any = None

    @validation_parameters
    def __init__(
        self,
        listen_event_name: str,
        function: Callable,
        me: Any,
        listen_path_str: str | list[str],
    ) -> None:
        """Constructor"""

        if isinstance(listen_path_str, str):
            self.listen_selectors = [Selector(listen_path_str)]
        if isinstance(listen_path_str, list):
            self.listen_selectors = []
            for p in listen_path_str:
                self.listen_selectors.append(Selector(p))

        self.listen_event_name = listen_event_name
        self.function = function
        self.me = me
        self.trigg_path = []

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.listen_selectors = self.listen_selectors
        result.listen_event_name = self.listen_event_name
        result.me = self.me
        result.function = self.function

        return result

    def __str__(self):
        return f"StrictoEvent({self.listen_event_name}, {self.listen_selectors})"

    def match_selectors(self, origin_selector: Selector) -> bool:
        """Check if origin_selector is in the list of selector (or a parent)

        :param origin_selector: _description_
        :type origin_selector: Selector
        :return: _description_
        :rtype: bool
        """
        # (f'Match selector {origin_selector} with {self.listen_selectors}')
        for p in self.listen_selectors:
            if origin_selector <= p:
                return True
        return False

    def trigg(self, root: Any, **kwargs) -> None:
        """Trigg the event function if the origin selector
        is included in the listen_path selector

        :param root: The root object
        :type root: Generic
        """

        remapped_me = root.select(self.me.path_name())
        if remapped_me is None:
            return

        self.function(self.listen_event_name, root, remapped_me, **kwargs)


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

    def register_event(
        self, me: Any, listen_event_name: str, function: Callable
    ) -> None:
        """Register an event

        :param event: The event to register
        :type event: StrictoEvent
        """
        # Create events per id
        my_id = id(me)
        if my_id not in self._events_per_object:
            self._events_per_object[my_id] = {}

        events = self._events_per_object[my_id]

        if listen_event_name not in events:
            events[listen_event_name] = []
        events[listen_event_name].append(function)

    def free_events(self, me: Any) -> None:
        """Erase events for this root object

        :param me: me
        :type me: GenericType
        """
        my_id = id(me)
        if my_id in self._events_per_object:
            del self._events_per_object[my_id]

    def copy_object_id(self, src_id: int, dst_id: int) -> None:
        """Copy event when an object is copied

        :param src_id: _description_
        :type src_id: int
        :param dst_id: _description_
        :type dst_id: int
        """
        if src_id not in self._events_per_object:
            return

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

        my_id = id(me)

        if my_id in self._events_per_object:
            events = self._events_per_object[my_id]
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


eventManager = SingletonEventManager()
