from grokcore.security import Permission
from grokcore.component import name


class DefaultPermission(Permission):
    """Default permission set as a fallback for unprotected classes.
    """
    name("grok.View")
