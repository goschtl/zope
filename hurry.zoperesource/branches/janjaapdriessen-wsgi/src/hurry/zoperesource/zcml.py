from zope.interface import Interface
from zope import component
from zope.publisher.interfaces.browser import IBrowserRequest
import hurry.resource
from hurry.zoperesource.zopesupport import HurryResource

def action_setup(_context):
    """Publish all hurry.resource library entry points as resources.
    """
    for library in hurry.resource.libraries():
        def factory(request):
            return HurryResource(request, library)
        adapts = (IBrowserRequest,)
        provides = Interface

        _context.action(
            discriminator = ('adapter', adapts, provides, library.name),
            callable = component.provideAdapter,
            args = (factory, adapts, provides, library.name))

