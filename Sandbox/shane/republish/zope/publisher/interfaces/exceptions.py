
from zope.interface import Interface
from zope.interface.common.interfaces import IException, ILookupError

__all__ = (
    'IPublishingException',
    'PublishingException',
    'ITraversalException',
    'TraversalException',
    'INotFound',
    'NotFound',
    'IDebugError',
    'DebugError',
    'IBadRequest',
    'BadRequest',
    'IRetry',
    'Retry',
    'IExceptionSideEffects',
    )

class IPublishingException(IException):
    pass

class PublishingException(Exception):
    implements(IPublishingException)

class ITraversalException(IPublishingException):
    pass

class TraversalException(PublishingException):
    implements(ITraversalException)

class INotFound(ILookupError, ITraversalException):
    def getObject():
        'Returns the object that was being traversed.'

    def getName():
        'Returns the name that was being traversed.'

class NotFound(LookupError, TraversalException):
    implements(INotFound)

    def __init__(self, ob, name, request=None):
        self.ob = ob
        self.name = name

    def getObject(self):
        return self.ob

    def getName(self):
        return self.name

    def __str__(self):
        try:
            ob = `self.ob`
        except:
            ob = 'unprintable object'
        return 'Object: %s, name: %s' % (ob, `self.name`)

class IDebugError(ITraversalException):
    def getObject():
        'Returns the object being traversed.'

    def getMessage():
        'Returns the debug message.'

class DebugError(TraversalException):
    implements(IDebugError)

    def __init__(self, ob, message):
        self.ob = ob
        self.message = message

    def getObject(self):
        return self.ob

    def getMessage(self):
        return self.message

    def __str__(self):
        return self.message

class IBadRequest(IPublishingException):
    def __str__():
        'Returns the error message.'

class BadRequest(PublishingException):

    implements(IBadRequest)

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class IRetry(IPublishingException):
    def getOriginalException():
        'Returns the original exception object.'

class Retry(PublishingException):
    """Raise this to retry a request."""

    implements(IRetry)

    def __init__(self, orig_exc=None):
        """orig_exc must be a 3-tuple as returned from sys.exc_info() or None"""
        self.orig_exc = orig_exc

    def getOriginalException(self):
        return self.orig_exc

    def __str__(self):
        if self.orig_exc is None:
            return 'None'
        return str(self.orig_exc[1])

class IExceptionSideEffects(Interface):
    """An exception caught by the publisher is adapted to this so that
    it can have persistent side-effects."""

    def __call__(obj, request, exc_info):
        """Effect persistent side-effects.

        Arguments are:
          obj                 context-wrapped object that was published
          request             the request
          exc_info            the exception info being handled

        """
