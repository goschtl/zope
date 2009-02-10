

class IPublishTraverse(Interface):

    def publishTraverse(request, name):
        """Lookup a name

        The 'request' argument is the publisher request object.  The
        'name' argument is the name that is to be looked up; it must
        be an ASCII string or Unicode object.

        If a lookup is not possible, raise a NotFound error.

        This method should return an object having the specified name and
        `self` as parent. The method can use the request to determine the
        correct object.
        """

class IHTTPPublisher(IPublishTraverse):
    """HTTP-specific publisher traversal"""

class IBrowserPublisher(IPublishTraverse):

    def browserDefault(request):
        """Provide the default object

        The default object is expressed as a (possibly different)
        object and/or additional traversal steps.

        Returns an object and a sequence of names.  If the sequence of
        names is not empty, then a traversal step is made for each name.
        After the publisher gets to the end of the sequence, it will
        call browserDefault on the last traversed object.

        Normal usage is to return self for object and a default view name.

        The publisher calls this method at the end of each traversal path. If
        a non-empty sequence of names is returned, the publisher will traverse
        those names and call browserDefault again at the end.

        Note that if additional traversal steps are indicated (via a
        nonempty sequence of names), then the publisher will try to adjust
        the base href.
        """

class IBrowserPage(IBrowserPublisher):
    """Browser page"""

    def __call__(*args, **kw):
        """Compute a response body"""

class IBrowserView(IView):
    """Browser View"""

class IDefaultBrowserLayer(IBrowserRequest):
    """The default layer."""
