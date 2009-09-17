from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 layer.
       If you need to register a viewlet only for the
       "Grok theme for Plone 3" skin, this interface must be its layer
       (in grok/viewlets/configure.zcml).
    """
