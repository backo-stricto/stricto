"""
File that defines the ACL class, which is used to manage access control lists 
for allowing or restricting domains for emails and urls
"""
import re

from typing import List, Optional

class ACL:
    """
    An ACL is a structure composed by :
    - a list of raw strings that are used for matching a domain
    - a boolean that indicates if the ACL is a whitelist (allow only the domains that match) or a blacklist (block the domains that match)
    """
    def __init__(self, patterns: List[str], is_whitelist: bool):
        self.patterns = []
        for pattern in patterns:
            "compile the pattern to check if it's a valid regex, if not raise an exception"
            "and store the compiled pattern in the ACL for faster matching"
            try:
                compiled = re.compile(pattern)
                self.patterns.append(compiled)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {pattern}") from e
        self.is_whitelist = is_whitelist

    def __str__(self):
        return f"ACL(patterns={self.patterns}, is_whitelist={self.is_whitelist})"

    def __repr__(self):
        return self.__str__()
    
    def is_allowed(self, domain: str) -> bool:
        """
        Check if a domain is allowed by the ACL by matching the domain strings against every pattern in the ACL. 
        If a pattern matches, the result is determined by the is_whitelist flag. 
        If no pattern matches, the result is the opposite of the is_whitelist flag.
        The checks stop at the first match of a whitelist pattern or the first match of a blacklist pattern, so the order of the patterns in the ACL is important.
        """
        for pattern in self.patterns:
            if re.match(pattern, domain):
                return self.is_whitelist
        return not self.is_whitelist

    
    def add_pattern(self, pattern: str) -> None:
        """Add a pattern to the ACL
        """        
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {pattern}") from e
        self.patterns.append(compiled_pattern)

    def remove_pattern(self, pattern: str) -> None:
        """
        Remove a compiled pattern from the ACL. If the pattern is not found, raise a ValueError.
        """
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {pattern}") from e
        if compiled_pattern in self.patterns:
            self.patterns.remove(compiled_pattern)
        else:
            raise ValueError(f"Pattern not found in ACL: {pattern}")
    