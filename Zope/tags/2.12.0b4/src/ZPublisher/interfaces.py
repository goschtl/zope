from zope.interface import Interface, Attribute

#############################################################################
# Publication events
#  These are events notified in 'ZPublisher.Publish.publish'.

class IPubEvent(Interface):
    '''Base class for publication events.

    Publication events are notified in 'ZPublisher.Publish.publish' to
    inform about publications (aka requests) and their fate.
    '''
    request = Attribute('The request being affected')

class IPubStart(IPubEvent):
    '''Event notified at the beginning of 'ZPublisher.Publish.publish'.'''

class IPubEnd(IPubEvent):
    '''Event notified after request processing.

    Note that a retried request ends before the retrial, the retrial
    itself is considered a new event.
    '''

class IPubSuccess(IPubEnd):
    '''A successful request processing.'''

class IPubFailure(IPubEnd):
    '''A failed request processing.

    Note: If a subscriber to 'IPubSuccess' raises an exception,
    then 'IPubFailure' may be notified in addtion to 'IPubSuccess'.
    '''
    exc_info = Attribute('''The exception info as returned by 'sys.exc_info()'.''')
    retry = Attribute('Whether the request will be retried')


class IPubAfterTraversal(IPubEvent):
    """notified after traversal and an (optional) authentication."""


class IPubBeforeCommit(IPubEvent):
    """notified immediately before the transaction commit (i.e. after the main
    request processing is finished.
    """
