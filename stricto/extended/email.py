"""
Module email verify if valid
"""
import re
from stricto import Extend, SConstraintError


class Email(Extend):
    """Extend type that validates and stores an email address."""
    def __init__(self, **kwargs):
        super().__init__(str, **kwargs)

    def __json_encode__(self):

        va = self.get_value()
        if va is None:
            return None
        return str(self.get_value())

    def __json_decode__(self, value: str):
        return value

    def check_constraints(self, value: str):

        pattern1 = r"[A-Za-z0-9-.+]+.[A-Za-z0-9-.+]*"
        pattern2 = r"[A-Za-z0-9-.+]+.[A-Za-z]+"
        result = pattern1 + r"@" + pattern2
        verify = re.match(result, value)
        if verify is None:
            raise SConstraintError(
                '{0}:Must be a email (value="{value}")', self.path_name(), value=value
            )
        return True
