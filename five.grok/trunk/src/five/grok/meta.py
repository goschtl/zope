import martian
from five import grok

from Products.Five.security import protectClass
from Globals import InitializeClass as initializeClass

from grokcore.view.meta import ViewGrokkerBase

def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()

class ViewGrokker(ViewGrokkerBase):
    martian.component(grok.View)
    
    def execute(self, factory, config, context, layer, name, permission, **kw):
        if permission is None:
            permission = 'zope.Public'
            
        return super(ViewGrokker, self).execute(factory, config, context, layer, name, permission, **kw)
            
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
