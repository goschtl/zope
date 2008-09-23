from zope.interface import Interface, Attribute

class ILibrary(Interface):
    """A library contains one or more resources.

    A library has a unique name. It is expected to have multiple
    subclasses of the library class for particular kinds of resource
    libraries.
    """
    name = Attribute("The unique name of the library")

class IResourceInclusion(Interface):
    """Resource inclusion

    A resource inclusion specifies how to include a single resource in a
    library.
    """
    library = Attribute("The resource library this resource is in")
    relpath = Attribute("The relative path of the resource "
                        "within the resource library")
    rollups = Attribute("A list of potential rollup ResourceInclusions "
                        "that this resource is part of")

    def ext():
        """Get the filesystem extension of this resource.

        This is used to determine what kind of resource we are dealing
        with.
        """

    def mode(mode):
        """Get the resource inclusion in a different mode.

        mode - the mode (minified, debug, etc) that we want this
               resource to be in. None is the default mode, and is
               this resource spec itself.

        An IResourceInclusion for that mode is returned.
        
        If we cannot find a particular mode for a resource, the
        original resource inclusion is returned.
        """
        
    def key():
        """Returns a unique, hashable identifier for the resource inclusion.
        """

    def need():
        """Express need directly for the current INeededInclusions.

        This is a convenience method to help express inclusions more
        easily, just do myinclusion.need() to have it be included in
        the HTML that is currently being rendered.
        """

    def inclusions():
        """Get all inclusions needed by this inclusion, including itself.
        """

class INeededInclusions(Interface):
    """A collection of inclusions that are needed for page display.
    """

    def need(inclusion):
        """Add the inclusion to the list of needed inclusions.

        See also IInclusion.need() for a convenience method.
        """

    def inclusions(mode=None):
        """Give all resource inclusions needed.

        mode - optional argument that tries to put inclusions into
               a particular mode (such as debug, minified, etc)
               Has no effect if an included resource does not know
               about that mode; the original resource will be included.

        Returns a list of resource inclusions needed.
        """

    def render(self, mode=None):
        """Render all resource inclusions for HTML header.

        mode - optional argument that tries to put inclusions into
               a particular mode (such as debug, minified, etc).
               Has no effect if an included resource does not know
               about that mode; the original resource will be included.

        Returns a HTML snippet that includes the required resource inclusions.
        """

class ICurrentNeededInclusions(Interface):
    def __call__():
        """Return the current needed inclusions object.

        These can for instance be retrieved from the current request.
        """

class IInclusionUrl(Interface):
    def __call__(inclusion):
        """Return the URL for given resource inclusion.
        """
