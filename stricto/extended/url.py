# pylint: disable=duplicate-code
"""
Module for URL validation and parsing.
"""

from urllib.parse import urlsplit, SplitResult
from stricto.extend import Extend
from stricto import STypeError


class Url(Extend):
    """
    A specific class to play with URLs
    """

    def __init__(self, **kwargs):
        """
        initialisation. Must pass the type (SplitResult)
        """
        super().__init__(SplitResult, **kwargs)

    def __json_encode__(self):
        value = self.get_value()
        if value is None:
            return None
        return value.geturl()

    def __json_decode__(self, value: str) -> SplitResult:
        parsed = urlsplit(value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f'Value "{value}" must be a valid URL')
        return parsed

    def check_type(self, value):
        if isinstance(value, SplitResult):
            try:
                if not value.scheme or not value.netloc:
                    raise STypeError(f'Value "{value.geturl()}" must be a valid URL')
                return True
            except (ValueError, TypeError) as exception:
                raise STypeError(f'Value "{value.geturl()}" must be a valid URL') from exception
        else:
            raise STypeError(
                '{0}: Must be a valid URL (value="{value}")',
                self.path_name(),
                value=value,
            )
