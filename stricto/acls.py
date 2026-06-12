"""
List acl that search
"""

from stricto import ACL,Extend


class ACLS(Extend):
    """init list acl and default"""
    def __init__(self, acls: list[ACL], default: bool):
        self.acls = acls
        self.default = default

    def authorize(self, domain: str) -> bool:
        """
        verify a domain authorization
        """
        print(domain)
        for acl in self.acls:
            if self.default is False and acl.is_a_whitelist():
                if acl.accept(domain):
                    return True
            if self.default is True and acl.is_a_whitelist() is False:
                if acl.accept(domain) is False:
                    return False
        return self.default
