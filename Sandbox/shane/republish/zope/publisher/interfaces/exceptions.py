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
