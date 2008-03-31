Overview
========

This package implements a transaction-safe indexing dispatcher.

* Pluggable indexing architecture

* Indexing operations are deferred to right after the request has
ended, exhibiting asynchronous behavior. All operations are carried
out in the thread that committed the tranaction.

* The operation queue is optimized to avoid unnecessary indexing.

