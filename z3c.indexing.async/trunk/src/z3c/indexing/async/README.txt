z3c.indexing.async
==================

The asynchronous dispatcher passes operations on to a worker thread
which is initialized with a connection object.

Let's start the queue.

  >>> from z3c.indexing.async import queue
  >>> queue.QueueProcessor.FLUSH_TIMEOUT = 0.5
  >>> queue.QueueProcessor.start()
  <z3c.indexing.async.queue.QueueProcessor object at ...>

The asynchronous dispatcher leaves operations up to other
dispatchers. We'll provide a mock implementation and register it as a
component.

  >>> class MockDispatcher(object):
  ...     def __init__(self):
  ...          self.queue = []
  ...
  ...     def index(self, obj, attributes=None):
  ...         self.queue.append((obj, attributes))
  ...
  ...     def flush(self):
  ...         print "Flushing queue: %s" % str(self.queue)
  ...         del self.queue[:]
  
We'll provide this dispatcher for string items.
  
  >>> from z3c.indexing.dispatch.interfaces import IDispatcher
  >>> _dispatcher = MockDispatcher()
  >>> component.provideAdapter(
  ...     lambda *args: _dispatcher, (IDispatcher, str), IDispatcher)

  >>> from z3c.indexing.async.dispatcher import AsynchronousDispatcher
  >>> dispatcher = AsynchronousDispatcher()

Index some strings:
  
  >>> dispatcher.index('rabbit')
  >>> dispatcher.index('elephant')
    
Wait for the timeout (set to 0.5 seconds in this test)...

  >>> import time
  >>> time.sleep(0.6)
  Flushing queue: [('rabbit', None), ('elephant', None)]

Let's try and index another item and flush the queue manually:
  
  >>> dispatcher.index('snake')
  >>> dispatcher.flush()

Since the queue is running in its own thread, we'll want to sleep for
just a short while.

  >>> time.sleep(0.1)
  Flushing queue: [('snake', None)]  
  
Cleanup
-------

To be a good testing citizen, we cleanup our queue processing thread.
  
  >>> queue.QueueProcessor.stop()

