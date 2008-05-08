*************
Catalog Queue
*************

A catalog queue provides a queue for catalog indexing. The basic idea
is to queue catalog operations so:

- Operations can be batched for greater efficiency

- Application requests don't have to wait for indexing to be done

The benefits of queueing are especially significant when text indexes
are used.

.. contents::
