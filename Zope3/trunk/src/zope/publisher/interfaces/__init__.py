##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interfaces for the publisher.

$Id: __init__.py,v 1.2 2002/12/25 14:15:18 jim Exp $
"""

from zope.interface import Interface
from zope.interface import Attribute
from zope.exceptions import Unauthorized
from zope.exceptions import NotFoundError
from zope.component.interfaces import IPresentationRequest
from zope.interface.common.mapping import IEnumerableMapping


class PublishingException(Exception):
    pass


class TraversalException(PublishingException):
    pass


class NotFound(NotFoundError, TraversalException):

    def __init__(self, ob, name, request=None):
        self.ob = ob
        self.name = name

    def getObject(self):
        return self.ob

    def getName(self):
        return self.name

    def __str__(self):
        try: ob = `self.ob`
        except: ob = 'unprintable object'
        return 'Object: %s, name: %s' % (ob, `self.name`)


class DebugError(TraversalException):

    def __init__(self, ob, message):
        self.ob = ob
        self.message = message

    def getObject(self):
        return self.ob

    def getMessage(self):
        return self.message

    def __str__(self):
        return self.message


class BadRequest(PublishingException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Redirect(PublishingException):

    def __init__(self, location):
        self.location = location

    def getLocation(self):
        return self.location

    def __str__(self):
        return 'Location: %s' % self.location


class Retry (PublishingException):
    """Raise this to retry a request.
    """

    def __init__(self, orig_exc=None):
        self.orig_exc = orig_exc

    def getOriginalException(self):
        return self.orig_exc

    def __str__(self):
        return repr(self.orig_exc)


class IPublishTraverse(Interface):

    def publishTraverse(request, name):
        """Lookup a name

        The request argument is the publisher request object.
        """


def IPublisher(Interface):

    def publish(request):
        """Publish a request

        The request must be an IPublisherRequest.
        """


class IPublisherResponse(Interface):
    """Interface used by the publsher
    """

    def setBody(result):
        """Sets the response result value.
        """

    def handleException(exc_info):
        """Handles an otherwise unhandled exception.

        The publication object gets the first chance to handle an exception,
        and if it doesn't have a good way to do it, it defers to the
        response.  Implementations should set the reponse body.
        """

    def internalError():
        """Called when the exception handler bombs.

        Should report back to the client that an internal error occurred.
        """

    def outputBody():
        """Outputs the response to the client
        """

    def retry():
        """Returns a retry response

        Returns a response suitable for repeating the publication attempt.
        """


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

    def getApplication(request):
        """Returns the object where traversal should commence.
        """

    def callTraversalHooks(request, ob):
        """Invokes any traversal hooks associated with the object.
        """

    def traverseName(request, ob, name, check_auth=1):
        """Traverses to the next object.

        If check_auth is set,
        performs idenitification, authentication, and authorization.
        Returns the subobject.
        """

    def afterTraversal(request, ob):
        """Post-traversal hook.
        """

    def callObject(request, ob):
        """Call the object, returning the result.

        For GET/POST this means calling it, but for other methods
        (including those of WebDAV and FTP) this might mean invoking
        a method of an adapter.
        """

    def afterCall(request):
        """Post-callObject hook (if it was successful).
        """

    def handleException(object, request, exc_info, retry_allowed=1):
        """Handle an exception

        Either:
        - sets the body of the response, request.response, or
        - raises a Retry exception, or
        - throws another exception, which is a Bad Thing.

        Note that this method should not leak, which means that
        exc_info must be set to some other value before exiting the method.
        """


class IApplicationResponse(Interface):
    """Features that support application logic
    """

    def write(string):
        """Output a string to the response body.
        """


class IPublicationRequest(IPresentationRequest):
    """Interface provided by requests to IPublication objects
    """

    user = Attribute("""User object associated with the request

                        It is up to the publication object to set this
                        attribute.
                        """)

    response = Attribute("""the request's response object

        Return an IPublisherResponse for the request.
        """)

    def close():
        """Release resources held by the request.
        """

    def hold(object):
        """Hold a reference to an object until the request is closed
        """

    def getTraversalStack():
        """Return the request traversal stack

        This is a sequence of steps to traverse in reverse order. They
        will be traversed from last to first.
        """

    def setTraversalStack(stack):
        """Change the traversal stack.

        See getTraversalStack.
        """

    def getPositionalArguments():
        """Return the positional arguments given to the request.
        """

    def setViewSkin(skin):
        """Set the skin to be used for the request.

        It's up to the publication object to decide this.
        """


class IPublisherRequest(IPublicationRequest):
    """Request interface use by the publisher

    The responsibility of requests is to encapsulate protocol
    specific details, especially wrt request inputs.

    Request objects also serve as "context" objectsm providing
    construction of and access to responses and storage of publication
    objects.

    """

    def supportsRetry():
        """Check whether the request supports retry

        Return a boolean value indicating whether the request can be retried.
        """

    def retry():
        """Return a retry request

        Return a request suitable for repeating the publication attempt.
        """

    publication = Attribute("""the request's publication object

        The publication object, an IRequestPublication provides
        application-specific functionality hooks.
        """)

    def setPublication(publication):
        """Set the request's publication object
        """

    def traverse(object):
        """Traverse from the given object to the published object

        The published object is returned.

        The following hook methods on the publication will be called:

          - callTraversalHooks is called before each step and after
            the last step.

          - traverseName to actually do a single traversal

        """

    def processInputs():
        """Do any input processing that needs to bve done before traversing

        This is done after construction to allow the publisher to
        handle errors that arise.
        """


class IApplicationRequest(IEnumerableMapping):
    """Features that support application logic
    """

    user = Attribute("""User object associated with the request
                        This is a read-only attribute.
                        """)

    body = Attribute("""the body of the request as a string""")

    bodyFile = Attribute("""the body of the request as a file""")

    def __getitem__(key):
        """Return request data

        The only request data are envirnment variables.
        """

    environment = Attribute(
        """Request environment data

        This is a read-only mapping from variable name to value.
        """)
