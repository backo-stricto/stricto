"""
File that defines the ACL class, which is used to manage access control lists 
for allowing or restricting domains for emails and urls
"""
import re

class ACL:
    """
    An ACL is a structure composed by :
    - a compiled regex pattern that is used for matching a domain
    - a boolean that indicates if the ACL is a whitelist (allow only the domains that match) or a blacklist (block the domains that match)
    """
    def __init__(self, pattern:str, is_whitelist: bool):
        "compile the pattern to check if it's a valid regex, if not raise an exception"
        "and store the compiled pattern in the ACL for faster matching"
        try:
            self.pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {pattern}") from e
        self.is_whitelist = is_whitelist

    def __str__(self):
        return f"ACL(pattern={self.pattern}, is_whitelist={self.is_whitelist})"

    def __repr__(self):
        return self.__str__()
    
    def match(self, domain: str) -> bool:
        """
        Check if a domain is allowed by the ACL by matching the domain string against the compiled pattern.
        If a pattern matches, the result is determined by the is_whitelist flag.
        If no pattern matches, the result is the opposite of the is_whitelist flag.
        """
        if re.match(self.pattern, domain):
            return self.is_whitelist
        return not self.is_whitelist
    