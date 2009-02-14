from zope.interface import Interface

class IGrokSecurityViewPlaceholder(Interface):
    """A dummy interface in case we cannot import it from grok.

    This keeps us compatible with Grok versions < 1.0.
    """
    pass
