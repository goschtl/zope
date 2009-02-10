
"""The base interfaces for request and response objects."""

from zope.interface import Attribute
from zope.interface import Interface
from zope.interface.common.mapping import IExtendedReadMapping


class IRequest(IExtendedReadMapping):
    """Basic request data.

    The request object may be used as a mapping object, in which case
    values will be looked up in the order: [TODO].
    """

    environment = Attribute(
        """Request environment data.

        This is a pointer to the WSGI or CGI environment.
        """)

    traversal_path = Attribute(
        """Sequence of steps to traverse, where each step is a unicode.
        """)

    traversed = Attribute(
        """List of (name, obj) steps that were traversed.

        The first object is the application root and has an empty name.
        The last object is the object to call.
        """)

    response = Attribute(
        """The request's IResponse object
        """)

    positional_args = Attribute(
        """The positional arguments given to the request.
        """)

    principal = Attribute("""Principal object associated with the request.

    It should be an IPrincipal wrapped in its AuthenticationService's context.
    """)

    bodyStream = Attribute(
        """The stream that provides the data of the request.

        The data returned by the stream will not include any possible header
        information, which should have been stripped by the server (or
        previous layer) before.

        Also, the body stream might already be read and not return any
        data. This is commonly done when retrieving the data for the ``body``
        attribute.

        If you access this stream directly to retrieve data, it will not be
        possible by other parts of the framework to access the data of the
        request via the ``body`` attribute.""")

    debug = Attribute("""Debug flags (see IDebugFlags).""")

    annotations = Attribute(
        """Stores arbitrary application data under package-unique keys.

        By "package-unique keys", we mean keys that are are unique by
        virtue of including the dotted name of a package as a prefex.  A
        package name is used to limit the authority for picking names for
        a package to the people using that package.

        For example, when implementing annotations for hypothetical
        request-persistent adapters in a hypothetical zope.persistentadapter
        package, the key would be (or at least begin with) the following::

          "zope.persistentadapter"
        """)

    def hold(held):
        """Hold a reference to an object until the request is closed.

        The object should be an IHeld.  If it is an IHeld, its
        release method will be called when it is released.
        """

    def close():
        """Release resources held by the request.
        """

    def retry():
        """Returns a re-initialized request to be retried.

        Returns a request suitable for repeating the publication attempt,
        or raises RetryNotSupported if the response can not be retried.
        """


class IResponse(Interface):
    """Holds a response result."""

    def getStatus():
        """Returns the current status code as an integer.
        """

    def getStatusString():
        """Return the status followed by the reason."""

    def setStatus(status, reason=None):
        """Sets the status code of the response

        The status parameter must be either an integer (preferred)
        or a value that can be converted to an integer using the int()
        function,

        The reason parameter is a short message to be sent with the status
        code to the client.  If reason is not provided, a standard
        reason will be supplied, falling back to "Unknown" for unregistered
        status codes.
        """

    def setStandardStatus(name):
        """Sets the status of the response using a standard status name.

        The name will be converted to a code appropriate for the protocol.
        For example, the name "NotFound" when applied to an HTTP
        request will set the response status code to 404 and the name
        "OK" will set the status to 200.

        If the provided name is not recognized, the response status will
        be set to a generic error status code (for example,
        500 for HTTP).
        """

    def getHeaders():
        """Returns a sequence of header name, value tuples.

        If the protocol does not support headers, such as FTP, this
        method should return an empty sequence.
        """

    def setResult(result):
        """Sets response result value based on input.

        Input is usually a unicode string, a string, None, or an object
        that can be adapted to IResult with the request.  The end result
        is an iterable such as WSGI prefers, determined by following the
        process described below.

        Try to adapt the given input, with the request, to IResult
        (found elsewhere in this module).  If this fails, and the original
        value was a string, use the string as the result; or if was
        None, use an empty string as the result; and if it was anything
        else, raise a TypeError.

        If the result of the above (the adaptation or the default
        handling of string and None) is unicode, encode it (to the
        preferred encoding found by adapting the request to
        zope.i18n.interfaces.IUserPreferredCharsets, usually implemented
        by looking at the HTTP Accept-Charset header in the request, and
        defaulting to utf-8) and set the proper encoding information on
        the Content-Type header, if present.  Otherwise (the end result
        was not unicode) application is responsible for setting
        Content-Type header encoding value as necessary.

        If the result of the above is a string, set the Content-Length
        header, and make the string be the single member of an iterable
        such as a tuple (to send large chunks over the wire; see
        discussion in the IResult interface).  Otherwise (the end result
        was not a string) application is responsible for setting
        Content-Length header as necessary.

        Set the result of all of the above as the response's result. If
        the status has not been set, set it to an OK status (200 for HTTP).
        """

    def consumeBodyIter():
        """Returns the response body as an iterable.

        Note that this function can be only requested once, since it is
        constructed from the result.
        """

    def retry():
        """Returns a re-initialized response to be retried.

        Returns a response suitable for repeating the publication attempt,
        or raises RetryNotSupported if the response can not be retried.
        """


class IResult(Interface):
    """An iterable that provides the body data of the response.

    For simplicity, an adapter to this interface may in fact return any
    iterable, without needing to strictly have the iterable provide
    IResult.

    IMPORTANT: The result object may be held indefinitely by a server
    and may be accessed by arbitrary threads. For that reason the result
    should not hold on to any application resources (i.e., should not
    have a connection to the database) and should be prepared to be
    invoked from any thread.

    This iterable should generally be appropriate for WSGI iteration.

    Each element of the iteration should generally be much larger than a
    character or line; concrete advice on chunk size is hard to come by,
    but a single chunk of even 100 or 200 K is probably fine.

    If the IResult is a string, then, the default iteration of
    per-character is wildly too small.  Because this is such a common
    case, if a string is used as an IResult then this is special-cased
    to simply convert to a tuple of one value, the string.

    Adaptation to this interface provides the opportunity for efficient file
    delivery, pipelining hooks, and more.
    """

    def __iter__():
        """iterate over the values that should be returned as the result.

        See IHTTPResponse.setResult.
        """


class IHeld(Interface):
    """Object to be held and explicitly released by a request
    """

    def release():
        """Release the held object

        This is called by a request that holds the IHeld when the
        request is closed

        """

class IDebugFlags(Interface):
    """Features that support debugging."""

    sourceAnnotations = Attribute("""Enable ZPT source annotations""")
    showTAL = Attribute("""Leave TAL markup in rendered page templates""")

