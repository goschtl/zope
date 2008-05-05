from z3c.zrtresource.zcml import IZRTResourceDirective
from z3c.zrtresource.zcml import zrtresource
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.viewlet.metadirectives import IViewletDirective
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.metaconfigure import viewletDirective

class IZRTResourceViewletDirective(IViewletDirective, IZRTResourceDirective):
    """A directive to register a new zrtresource and viewlet at the same time.

    """


def zrtresourceViewlet(_context, name, file,
                       layer=IDefaultBrowserLayer,
                       permission='zope.Public', for_=Interface,
                       view=IBrowserView, manager=IViewletManager,
                       class_=None, template=None, attribute='render',
                       allowed_interface=None, allowed_attributes=None,
                       **kwargs):

    viewletDirective(_context, name, permission, for_=for_,
                     layer=layer, view=view, manager=manager,
                     class_=class_, template=template,
                     attribute=attribute,
                     allowed_interface=allowed_interface,
                     allowed_attributes=allowed_attributes,
                     resource=name, **kwargs)

    zrtresource(_context, name, file, layer=layer,
                permission=permission)
