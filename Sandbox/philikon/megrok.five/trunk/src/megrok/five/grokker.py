import grok
import Acquisition
import Products
from Products.Five.security import protectName, initializeClass

from zope import interface, component
from zope.security.checker import CheckerPublic

from grok import util, meta
import grok.interfaces
import megrok.five

class ViewGrokker(meta.ViewGrokker):

    priority = -1   # beat grok.meta.ViewGrokker
    # XXX this is weird, I should have to set a *higher* priority so
    # that I'm executed *before* grok.meta.ViewGrokker (which should
    # *never* be called at all).  Instead, I have to set a lower
    # priority so that I'm executed afterwards and *my* adapter
    # registration wins over his.  This is messed up.  FIXME

    def register(self, context, name, factory, module_info, templates):
        # Five views need to inherit from Acquisition currently, so
        # let's create a subclass of the view class and mix in
        # acquisition (evil, I know...)
        old_factory = factory
        factory = type(factory.__name__, (Acquisition.Explicit, factory),
                       # deep Zope 2 traversal voodoo here (traversed
                       # items need to have a __name__ property, apparently)
                       {'__name__': property(lambda self: self.__view_name__)})
        factory.__module__ = module_info.dotted_name

        super(ViewGrokker, self).register(context, name, factory, module_info,
                                          templates)

        # Do the Zope 2 security declarations (public by default, just
        # like in grok). Note that we don't need to do any sanity
        # checks here.  They have already been done at this point by
        # the super class.
        permissions = util.class_annotation(factory, 'grok.require', [])
        if not permissions or permissions[0] in ('zope.Public', 'zope2.Public'):
            permission = CheckerPublic
        else:
            permission = permissions[0]

        protectName(factory, '__call__', permission)
        initializeClass(factory)


class ApplicationGrokker(grok.ClassGrokker):
    component_class = grok.Application
    priority = 501
    continue_scanning = True

    def register(self, context, name, factory, module_info, templates):
        full_name = module_info.dotted_name + "." + name
        setattr(factory, 'meta_type', full_name)

        interfaces = tuple(interface.implementedBy(factory))
        info = {'name': full_name,
                'action': 'createapp?name=%s' % full_name,
                'product': 'Five',
                'permission': 'Add %s' % full_name,
                'visibility': 'Global',
                'interfaces': interfaces,
                'instance': factory,
                'container_filter': None}
        Products.meta_types += (info,)
