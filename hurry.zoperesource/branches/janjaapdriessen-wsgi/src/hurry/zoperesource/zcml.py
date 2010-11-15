from zope.interface import Interface
from zope import component
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security.checker import NamesChecker

from hurry import resource
from hurry.zoperesource.zopesupport import Plugin
from hurry.zoperesource.zopesupport import HurryDirectoryResourceFactory


def create_resource_factory(library):
    allowed_resource_names = ('GET', 'HEAD', 'publishTraverse',
                              'browserDefault', 'request', '__call__')

    allowed_resourcedir_names = allowed_resource_names + ('__getitem__', 'get')

    checker = NamesChecker(allowed_resourcedir_names)
    return HurryDirectoryResourceFactory(library.path, checker, library.name)

def action_setup(_context):
    """Publish all hurry.resource library entry points as resources.
    """
    resource.register_plugin(Plugin())

    for library in resource.libraries():
        resource_factory = create_resource_factory(library)
        adapts = (IBrowserRequest,)
        provides = Interface

        _context.action(
            discriminator = ('adapter', adapts, provides, library.name),
            callable = component.provideAdapter,
            args = (resource_factory, adapts, provides, library.name))

