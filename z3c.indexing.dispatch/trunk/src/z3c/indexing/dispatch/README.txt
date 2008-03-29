z3c.indexing.dispatch
=====================

The indexing dispatcher is the main entry point for indexing content.

A dispatcher must implement three basic operations (defined in the
``IDispatcher`` interface): index, reindex and unindex.

Dispatching flow
----------------

Dispatchers can perform indexing operations directly or defer work to
other dispatchers using the following lookup pattern:

  IDispatcher(self, obj) -> IDispatcher

Example dispatching flows:

  transactional dispatcher -> zcatalog
  transactional dispatcher -> async -> xapian

Transactional dispatching
-------------------------

The transactional dispatcher will queue indexing operations while
waiting for the transaction boundary; then pass the operations on to
the next set of dispatchers.
