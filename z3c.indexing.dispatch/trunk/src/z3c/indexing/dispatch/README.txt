z3c.indexing.dispatch
=====================

The indexing dispatcher is the main entry point for indexing content
using the ``z3c.indexing`` architecture.

A dispatcher must implement the three basic indexing operations
(defined in the ``IDispatcher`` interface), index, reindex and
unindex, as well as a flush-method.

Configuration
-------------

Dispatchers can perform indexing operations directly or defer work to
other dispatchers using the following lookup pattern:

  IDispatcher(self, obj) -> IDispatcher

Example dispatching flows:

  transactional dispatcher -> zcatalog
  transactional dispatcher -> custom filter -> xapian

Operation
---------

The transactional dispatcher will queue indexing operations and only
actually carry them out after the request has ended*. A transaction
manager makes sure the queue only contains operations corresponding to
a succesful transaction.

*) This is currently the only supported behavior; an option should be
 available to carry out operations before the request ends.
