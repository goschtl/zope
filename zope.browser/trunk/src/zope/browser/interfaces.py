##############################################################################
#
# Copyright (c) 2004-2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Shared dependency less Zope3 browser components.
"""
__docformat__ = 'restructuredtext'

from zope.interface import Attribute, Interface
from zope.interface.common.interfaces import IException, ILookupError


class IRequest(Interface):
    """A request is a directive sent by a browser to the server,
    to retrieve a resource. It consists of a location and a set of headers.
    This information is represented by the environment data.
    """
    form = Attribute("parsed GET or POST data")
    method = Attribute("HTTP method used to query the server.")

    environment = Attribute(
        "Request environment data. This is a read-only mapping "
        "from variable name to value.")


class IResponse(Interface):
    """A response is the result of the publishing process.
    This prototypes a very basic response item, that can be
    extended for more specific uses.
    """
    body = Attribute("body of the response")
    headers = Attribute("headers of the response")

    def getStatus(as_int=False):
        """returns the status of the response.
        """

    def redirect(url, status=None, trusted=False):
        """Sets the response for a redirect.
        """


class IPublisher(Interface):
    """A publisher is charged with the task to use a request to publish
    a resource. This is usually done by returning a response after a
    'traversal' operation.
    """

    def publish(request, *args, **kwargs):
        """Publish a request

        The request is expected to be an IRequest.
        """


class IPublishingException(IException):
    """A publishing exception is an exception raised during the publishing
    process. The handling of such exception is therefore handled mainly
    by the publisher itself, opposed to the other kind of exceptions that
    are to be handled at another stage or/and another component.
    """


class IRedirect(IPublishingException):
    """A redirect exception is a publishing exception that interrupt the
    publishing in order to return a redirect-aware response.
    """

    location = Attribute("Target location of the redirect")


class INotFound(ILookupError, IPublishingException):
    """An exception meaning that the looked up object has not been found
    during the publishing process.
    """


class IBadRequest(IPublishingException):
    """Bad request means the request is somehow malformed or erroneous.
    It must have the capabilities to expose the error message when printed.
    """

    def __str__():
        """Returns the error message.
        """


class IView(Interface):
    """Views are multi-adapters for context and request objects.
    """
    context = Attribute("The context object the view renders")
    request = Attribute("The request object driving the view")


class IBrowserView(IView):
    """Views which are specialized for requests from a browser

    o Such views are distinct from those generated via WebDAV, FTP, XML-RPC,
      etc..
    """


class IDefaultViewName(Interface):
    """A string that contains the default view name

    A default view name is used to select a view when a user hasn't
    specified one.
    """

    def __str__():
        """Returns the default view name.
        """


class IAdding(IBrowserView):
    """Multi-adapter interface for views which add items to containers.

    o The 'context' of the view must implement ``zope.container.IContainer``.
    """

    def add(content):
        """Add content object to context.

        Add using the name in `contentName`.

        Return the added object in the context of its container.

        If `contentName` is already used in container, raise
        ``zope.container.interfaces.DuplicateIDError``.
        """

    contentName = Attribute(
         """The content name, usually set by the Adder traverser.

         If the content name hasn't been defined yet, returns ``None``.

         Some creation views might use this to optionally display the
         name on forms.
         """
         )

    def nextURL():
        """Return the URL that the creation view should redirect to.

        This is called by the creation view after calling add.

        It is the adder's responsibility, not the creation view's to
        decide what page to display after content is added.
        """

    def nameAllowed():
        """Return whether names can be input by the user.
        """

    def addingInfo():
        """Return add menu data as a sequence of mappings.

        Each mapping contains 'action', 'title', and possibly other keys.

        The result is sorted by title.
        """

    def isSingleMenuItem():
        """Return whether there is single menu item or not."""

    def hasCustomAddView():
        "This should be called only if there is `singleMenuItem` else return 0"


class ITerms(Interface):
    """Adapter providing lookups for vocabulary terms.
    """
    def getTerm(value):
        """Return an ITitledTokenizedTerm object for the given value

        LookupError is raised if the value isn't in the source
        """

    def getValue(token):
        """Return a value for a given identifier token

        LookupError is raised if there isn't a value in the source.
        """


class ISystemErrorView(Interface):
    """Error views that can classify their contexts as system errors
    """

    def isSystemError():
        """Return a boolean indicating whether the error is a system errror
        """
