Second-generation demo storage
==============================

The zc.demostorage2 module provides a storage implementation that
wraps two storages, a base storage and a storage to hold changes.
The base storage is never written to.  All new records are written to
the changes storage.  Both storages are expected to:

- Use packed 64-bit unsigned integers as object ids,

- Allocate object ids sequentially, starting from 0, and

- in the case of the changes storage, accept object ids assigned externally.

In addition, it is assumed that less than 2**62 object ids have been
allocated in the first storage.

Note that DemoStorage also assumes that it's base storage uses 64-bit
unsigned integer object ids allocated sequentially.

.. contents::
