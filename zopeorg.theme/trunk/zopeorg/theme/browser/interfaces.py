from zope.viewlet.interfaces import IViewletManager
from zope.interface import Interface

from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer.
    """

class IZopeorgPortalFooter(IViewletManager):
    """A viewlet manager that sits in the portal footer
       of zope.org site. Contains siteactions and copyright
    """
    
class IFeature(Interface):
    """ Marker interface for Feature content type
    """
    
class IFeatureView(IViewletManager):
    """ A viewlet manager is used for Feature view. Contains Blurb, feature's
        icon, featre's divider and so on
    """
    
