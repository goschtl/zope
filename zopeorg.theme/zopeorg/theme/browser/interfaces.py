from zope.viewlet.interfaces import IViewletManager

from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer.
    """

class IZopeorgPortalFooter(IViewletManager):
    """A viewlet manager that sits in the portal footer
       of zope.org site. Contains siteactions and copyright
    """
