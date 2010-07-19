from zope import component
from hurry.resource import interfaces

class Plugin(object):
    """Zope Component Architecture implementation of plugin.

    This implementation lets you register a utility that
    implements (in its __call___) get_current_needed_inclusions
    and an adapter that implements get_library_url().
    """
    def get_current_needed_inclusions(self):
        return component.getUtility(interfaces.ICurrentNeededInclusions)()

    def get_library_url(self, library):
        return interfaces.ILibraryUrl(library)
