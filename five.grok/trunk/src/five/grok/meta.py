import martian
import five.grok
import grokcore.security

from Products.Five.security import protectClass
from Globals import InitializeClass as initializeClass


class ViewSecurityGrokker(martian.ClassGrokker):
    martian.component(five.grok.View)
    martian.directive(grokcore.security.require, name='permission')
    
    def execute(self, factory, config, permission, **kw):
        if permission is None:
            permission = 'zope.Public'

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

        return True
