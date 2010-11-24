from zope.interface import Interface
from zope import component
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security.checker import NamesChecker
import hurry.resource
from hurry.zoperesource.zopesupport import HurryDirectoryResourceFactory

def create_resource_factory(library):
    allowed_names = (
        'GET',
        'HEAD',
        '__call__',
        '__getitem__',
        'browserDefault',
        'get',
        'publishTraverse',
        'request',
        )
    checker = NamesChecker(allowed_names)
    return HurryDirectoryResourceFactory(library, checker)

def action_setup(_context):
    """Publish all hurry.resource library entry points as resources.
    """
    for library in hurry.resource.libraries():
        resource_factory = create_resource_factory(library)
        adapts = (IBrowserRequest,)
        provides = Interface

        _context.action(
            discriminator = ('adapter', adapts, provides, library.name),
            callable = component.provideAdapter,
            args = (resource_factory, adapts, provides, library.name))

