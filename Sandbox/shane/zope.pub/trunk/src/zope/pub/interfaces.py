
from zope.interface import Interface

class IPublication(Interface):
    """Object publication framework.

    The responsibility of publication objects is to provide
    application hooks for the publishing process. This allows
    application-specific tasks, such as connecting to databases,
    managing transactions, and setting security contexts to be invoked
    during the publishing process.
    """
    # The order of the hooks mostly corresponds with the order in which
    # they are invoked.

    def beforeTraversal(request):
        """Pre-traversal hook.

        This is called *once* before any traversal has been done.
        """

    def getObject(request):
        """Traverses to the object and returns it.
        """

    def callTraversalHooks(request, ob):
        """Invokes any traversal hooks associated with the object.

        This is called before traversing each object.  The ob argument
        is the object that is about to be traversed.
        """

    def traverseName(request, ob, name):
        """Traverses to the next object.

        Name must be an ASCII string or Unicode object."""

    def afterTraversal(request, ob):
        """Post-traversal hook.

        This is called after all traversal.
        """

    def callObject(request, ob):
        """Call the object, returning the result.

        For GET/POST this means calling it, but for other methods
        (including those of WebDAV and FTP) this might mean invoking
        a method of an adapter.
        """

    def afterCall(request, ob):
        """Post-callObject hook (if it was successful).
        """

    def handleException(object, request, exc_info, retry_allowed=1):
        """Handle an exception

        Either:
        - sets the body of the response, request.response, or
        - raises a Retry exception, or
        - throws another exception, which is a Bad Thing.
        """

    def endRequest(request, ob):
        """Do any end-of-request cleanup
        """

