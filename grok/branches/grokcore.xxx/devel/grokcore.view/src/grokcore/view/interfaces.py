from zope import interface

from zope.publisher.interfaces.browser import IBrowserPage, IBrowserView


class IGrokView(IBrowserPage, IBrowserView):
    """Grok views all provide this interface."""

    context = interface.Attribute('context', "Object that the view presents.")

    request = interface.Attribute('request', "Request that the view was looked"
                                  "up with.")

    response = interface.Attribute('response', "Response object that is "
                                   "associated with the current request.")

    static = interface.Attribute('static', "Directory resource containing "
                                 "the static files of the view's package.")

    def redirect(url):
        """Redirect to given URL"""

    def url(obj=None, name=None, data=None):
        """Construct URL.

        If no arguments given, construct URL to view itself.

        If only obj argument is given, construct URL to obj.

        If only name is given as the first argument, construct URL
        to context/name.

        If both object and name arguments are supplied, construct
        URL to obj/name.

        Optionally pass a 'data' keyword argument which gets added to the URL
        as a cgi query string.
        """

    def default_namespace():
        """Returns a dictionary of namespaces that the template
        implementation expects to always be available.

        This method is *not* intended to be overridden by application
        developers.
        """

    def namespace():
        """Returns a dictionary that is injected in the template
        namespace in addition to the default namespace.

        This method *is* intended to be overridden by the application
        developer.
        """

    def update(**kw):
        """This method is meant to be implemented by grok.View
        subclasses.  It will be called *before* the view's associated
        template is rendered and can be used to pre-compute values
        for the template.

        update() can take arbitrary keyword parameters which will be
        filled in from the request (in that case they *must* be
        present in the request)."""

    def render(**kw):
        """A view can either be rendered by an associated template, or
        it can implement this method to render itself from Python.
        This is useful if the view's output isn't XML/HTML but
        something computed in Python (plain text, PDF, etc.)

        render() can take arbitrary keyword parameters which will be
        filled in from the request (in that case they *must* be
        present in the request)."""

    def application_url(name=None):
        """Return the URL of the closest application object in the
        hierarchy or the URL of a named object (``name`` parameter)
        relative to the closest application object.
        """
