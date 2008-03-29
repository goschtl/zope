from zope.interface import Interface

class IDispatcher(Interface):
    """Interface for dispatching indexing operations.

    Defines basic indexing operations corresponding to content being
    added, modified or deleted.
    """

    def index(obj, attributes=None):
        """Queue an index operation for the given object and attributes."""

    def reindex(obj, attributes=None):
        """Queue a reindex operation for the given object and attributes."""

    def unindex(obj):
        """Queue an unindex operation for the given object."""

    def flush(obj):
        """Flush queue."""
        

class ITransactionalDispatcher(IDispatcher):
    """A transactional dispatcher will keep operations in a queue
    until a transaction boundary."""
    
    def commit():
        """Commit transaction."""

    def clear():
        """Clear internal state and release transaction manager."""

    def getState():
        """Return copy of queue state."""

    def setState(state):
        """Set queue state."""

    
class IQueueReducer(Interface):
    """Operation queue optimization.

    This component might be merged with the transactional dispatcher
    at some point. The motivation for splitting this functionality out
    seems to primarily be a matter of optional configuration.
    """

    def optimize(queue):
        """Remove redundant entries from queue.

        The provided ``queue`` should be a sequence of operations on
        the form:

           (operator, object, attributes)

        An optimized sequence is returned.
        """
