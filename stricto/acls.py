"""
List acl that search
"""

from .acl import ACL


class ACLS:
    """init list acl and default"""

    def __init__(self, acls: list[ACL], default: bool):
        self.acls = acls
        self.default = default

    def authorize(self, value_to_verify: str) -> bool:
        """
        verify an authorization
        """
        for acl in self.acls:
            if self.default is False and acl.is_a_whitelist():
                if acl.accept(value_to_verify):
                    return True
            if self.default is True and acl.is_a_whitelist() is False:
                if acl.accept(value_to_verify) is False:
                    return False
        return self.default

    def __repr__(self):
        return f"ACLS({self.acls}) *={self.default}"
