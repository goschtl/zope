Blob File
=========

This package provides an implementation of zope.app.file.interfaces.IFile
which uses the Blob support introduced in ZODB 3.8. It's main purpose
is to provide an easy migration path for existing instances. For more
advanced file implementations see zope.file and z3c.extfile. 

The standard implementation in zope.app.file uses chunk objects to
break big files into manageable parts. These chunks flow the server caches 
whereas blobs are directly consumed by the publisher. The main difference
between this blob implementation and the old zope.app.file implementation
can be seen in a replacement of the chunk objects by Blobs.

