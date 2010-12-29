===================================================
dozodb, a dojo and ZODB-based application framework
===================================================

Dozodb facilites building dojo applications using data stored in the
ZODB.  It provides a full dojo storage implementation with lazy
loading.  It doesn't provide automatic object deactivation.

To use a storage, instantiate zc.dozodb.Store, passing an options
argument that includes the URL of a server resource.  If building
your own server resource, see the file protocol.txt in the source
Python package.

=======
Changes
=======

0.1.0 (yyyy-mm-dd)
==================
