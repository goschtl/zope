from zope import interface
from zope import component

from zope.app.component.back35 import LayerField
from zope.configuration.fields import Tokens, GlobalObject
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema import TextLine

from manager import ResourceManager
from interfaces import IResourceManager

managers = {}

class IResourceIncludeDirective(interface.Interface):
    include = Tokens(
        title=u"Files to include",
        description=u"The files containing the resource data.",
        required=True,
        value_type=TextLine())

    base = TextLine(
        title=u"Base path for includes",
        required=False)
    
    layer = LayerField(
        title=u"The layer the resource should be found in",
        description=u"""
        For information on layers, see the documentation for the skin
        directive. Defaults to "default".""",
        required=False
        )

    manager = GlobalObject(
        title=u"Include manager",
        required=False)
       
def includeDirective(_context, include, base=u"", layer=IDefaultBrowserLayer, manager=None):
    if base:
        include = [base+'/'+name for name in include]
        
    _context.action(
        discriminator = ('resourceInclude', IBrowserRequest, layer, "".join(include)),
        callable = handler,
        args = (include, layer, manager, _context.info),
        )

def handler(include, layer, manager, info):
    """Set up includes."""

    global managers

    if manager is None:
        manager = managers.get(layer)

        if manager is None:
            managers[layer] = manager = ResourceManager()

            count = len(managers)
            name = str(count).rjust(3, '0') + ':' + layer.__module__ + '.' + layer.__name__

            component.provideAdapter(
                manager, (layer,), IResourceManager, name=name)

    for path in include:
        manager.add(path)
