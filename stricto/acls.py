"""
List acl that search
"""

from stricto import ACL


class ACLS:
    def __init__(self, acls: list[ACL], default: bool):
        self.acls = acls
        self.default = default

    def authorize(self, domain: str) -> bool:
        """
        verify a domain authorization
        """
        print(domain)
        for acl in self.acls:
            print(acl)
            print(acl.accept(domain))
            print("whitlist", acl.is_a_whitelist())
            if self.default is False and acl.is_a_whitelist():
                if acl.accept(domain):
                    print("whitelist accept")
                    return True
            if self.default is True and acl.is_a_whitelist() is False:
                print("pass blacklist")
                if acl.accept(domain) is False:
                    print("blacklist don't accept")
                    return False
        return self.default
