ZODB tracing
============

Package is meant to aid debugging/tracing ZODB.
A special case was to determine from which point of the application
a huge amount of object loading comes.

TracingStorage:
---------------
A ZODB storage that allows tracing the calls going to the real storage.
Should be able to trace any type of storage.
Emits events using zope.notify on method calls.
A `statCollector` object can be installed, which can collect data.

Sample usage::

	collector = textStatCollector('/tmp/1.txt')
	storage     = TracingStorage(FileStorage.FileStorage(Path),
								 statCollector=coll)
    #instead of this:
	#storage     = FileStorage.FileStorage(Path)
    
	db          = DB(storage,
					 pool_size=pool_size,
					 cache_size=cache_size)
	connection  = db.open(transaction_manager=tm)
	root        = connection.root()
	return (root,connection,db,storage,tm)

Usage with Zope::

N/A yet, ZConfig has to be modified!

textStatCollector:
------------------
`statCollector` class to dump _every_ possible data regarding the method call
to a text file. Be careful, that will be a HUGE amount of data!