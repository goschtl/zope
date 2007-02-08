from zope import component
from zope.app.container.interfaces import INameChooser
from OFS.interfaces import IObjectManager
import grok.interfaces

class CreateApp(grok.View):
    """
    Instantiates megrok.five.Application objects.  Meant to be invoked
    from the ZMI add menu.
    """
    grok.context(IObjectManager)

    def render(self, name):
        factory = component.getUtility(grok.interfaces.IApplication, name=name)
        obj = factory()
        name = INameChooser(self.context).chooseName('', obj)
        obj.id = name # Zope 2 wants objects to have an id attribute
        self.context._setObject(name, obj)

        self.redirect(self.url('manage_main'))
