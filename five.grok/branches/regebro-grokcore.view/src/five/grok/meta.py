import martian
from martian import util
from martian.error import GrokError
from zope import interface, component
from zope.publisher.interfaces.browser import (IDefaultBrowserLayer,
                                               IBrowserRequest,
                                               IBrowserSkinType)
from five import grok

from Products.Five.security import protectClass
from Globals import InitializeClass as initializeClass

from grokcore.view import templatereg
from grokcore.view.meta import ViewGrokkerBase

def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()

class ViewGrokker(ViewGrokkerBase):
    martian.component(grok.View)
    
    def execute(self, factory, config, context, layer, name, permission, **kw):
        if permission is None:
            permission = 'zope.Public'
            
        return super(ViewGrokker, self).execute(factory, config, context, layer, name, permission, **kw)
            
    def checkTemplates(self, templates, module_info, factory):
        def has_render(factory):
            # XXX We haven't implemented GrokForm yet
            return (getattr(factory, 'render', None))
                    #and
                    #not util.check_subclass(factory, grok.components.GrokForm))
        def has_no_render(factory):
            return not getattr(factory, 'render', None)
        templates.checkTemplates(module_info, factory, 'view',
                                 has_render, has_no_render)

    def protectName(self, config, factory, permission):
        config.action(
            discriminator = ('five:protectClass', factory),
            callable = protectClass,
            args = (factory, permission)
            )

        # Protect the class
        config.action(
            discriminator = ('five:initialize:class', factory),
            callable = initializeClass,
            args = (factory,)
            )

class SkinGrokker(martian.ClassGrokker):
    martian.component(grok.Skin)
    martian.directive(grok.layer, default=IBrowserRequest)
    martian.directive(grok.name, get_default=default_view_name)

    def execute(self, factory, config, name, layer, **kw):
        config.action(
            discriminator=('skin', name),
            callable=component.interface.provideInterface,
            args=(name, layer, IBrowserSkinType)
            )
        return True


import grokcore.component
class PageTemplateFileFactory(grokcore.component.GlobalUtility):

    grokcore.component.implements(grokcore.view.interfaces.ITemplateFileFactory)
    grokcore.component.name('pt')

    def __call__(self, filename, _prefix=None):
        return grokcore.view.components.PageTemplate(filename=filename, _prefix=_prefix)
