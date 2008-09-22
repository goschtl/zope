from zope.interface import Interface, Attribute

class ILibrary(Interface):
    """A library contains one or more resources.

    A library has a unique name. It is expected to have multiple
    subclasses of the library class for particular kinds of resource
    libraries.
    """
    name = Attribute("The unique name of the library")

class IResourceSpec(Interface):
    """Resource specification

    A resource specification specifies a single resource in a library.
    """
    library = Attribute("The resource library this resource is in")
    relpath = Attribute("The relative path of the resource "
                        "within the resource library")

    def ext():
        """Get the filesystem extension of this resource.

        This is used to determine what kind of resource we are dealing
        with.
        """

    def mode(mode):
        """Get the resource in a different mode.

        mode - the mode (minified, debug, etc) that we want this
               resource to be in. None is the default mode, and is
               this resource spec itself.

        An IResourceSpec for that mode is returned.
        
        If we cannot find a particular mode for a resource, the
        resource spec is also used.
        """

    def consolidated():
        """Get the resource spec in consolidated form.

        A resource can be part of a larger resource, for instance
        multiple CSS files or .js files concatenated to each
        other. This is done for performance reasons to cut down on the
        amount of requests.

        Returns the resource spec of the consolidated resource, or
        None if no such larger resource is known.
        """
        
    def key():
        """Returns a unique, hashable identifier for the resource.
        """

class IInclusion(Interface):
    """A resource inclusion.

    This represents one or more resources that are included on a page
    together (in the HTML head section). An inclusion may have
    dependencies on other inclusions.
    """
    def depth():
        """The depth of the inclusion tree.

        This is used to sort the inclusions. If multiple inclusions are
        required on a page, the ones with the deepest inclusion trees
        are sorted first.
        """

    def resources_of_ext(ext):
        """Retrieve all resources with a certain extension in this inclusion.

        This also goes up to all inclusions that this inclusion depends on.
        """
        
    def need():
        """Express need directly for the current INeededInclusions.

        This is a convenience method to help express inclusions more
        easily, just do myinclusion.need() to have it be included in
        the HTML that is currently being rendered.
        """

class INeededInclusions(Interface):
    """A collection of inclusions that are needed for page display.
    """

    def need(inclusion):
        """Add the inclusion to the list of needed inclusions.

        See also IInclusion.need() for a convenience method.
        """

    def resources(mode=None):
        """Give all resources needed.

        mode - optional argument that tries to put inclusions into
               a particular mode (such as debug, minified, etc)
               Has no effect if an included resource does not know
               about that mode; the original resource will be included.

        Returns a list of resource specifications needed.
        """

    def render(self, mode=None):
        """Render all resources

        mode - optional argument that tries to put inclusions into
               a particular mode (such as debug, minified, etc).
               Has no effect if an included resource does not know
               about that mode; the original resource will be included.

        Returns a HTML snippet that includes the required resources.
        """
        
        
class ICurrentNeededInclusions(Interface):
    def __call__():
        """Return the current needed inclusions object.

        These can for instance be retrieved from the current request.
        """

class IResourceUrl(Interface):
    def __call__(resource):
        """Return the URL for given resource spec.
        """
