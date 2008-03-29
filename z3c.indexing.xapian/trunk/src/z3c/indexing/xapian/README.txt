z3c.indexing.xapian
===================

Let's set up some content.

  >>> rabbit = Content(title=u"rabbit", description="furry little creatures")
  >>> elephant = Content(title=u"elephant", description="large mammals with memory")
  >>> snake = Content(title=u"snake", description="reptile with scales")   

Set up component lookup.

  >>> from zope.component.interfaces import IComponentLookup
  >>> component.provideAdapter(
  ...     lambda context: component.getSiteManager(), (Content,), IComponentLookup)
  
Setting up an indexer connection
--------------------------------

To index a given object, the dispatcher needs to be able to locate an
indexer connection utility, identified by the interface
``IIndexerConnection``.
  
We'll provide the utility globally:

  >>> import xappy
  >>> indexer = xappy.IndexerConnection('tmp.idx')

  >>> from z3c.indexing.xapian.interfaces import IIndexerConnection
  >>> component.provideUtility(indexer, IIndexerConnection)
  
Let's add field actions corresponding to our example content object.
  
  >>> indexer.add_field_action('title', xappy.FieldActions.INDEX_FREETEXT )
  >>> indexer.add_field_action('title', xappy.FieldActions.STORE_CONTENT )
  >>> indexer.add_field_action('description', xappy.FieldActions.INDEX_FREETEXT )  

Next we set up an adapter that provides a Xapian document for our content.

  >>> def createXapianDocument(obj):
  ...     doc = xappy.UnprocessedDocument()
  ...     doc.id = obj.title
  ...     doc.fields.append(xappy.Field('title', obj.title))
  ...     doc.fields.append(xappy.Field('description', obj.description))
  ...     return doc

  >>> from z3c.indexing.xapian.interfaces import IDocument
  >>> component.provideAdapter(createXapianDocument, (Content,), IDocument)

  >>> IDocument(rabbit)
  UnprocessedDocument(u'rabbit',
      [Field('title', u'rabbit'), Field('description', 'furry little creatures')])
      
Dispatch
--------

  >>> from z3c.indexing.xapian.dispatcher import XapianDispatcher
  >>> dispatcher = XapianDispatcher()

Let's index some content.
  
  >>> dispatcher.index(rabbit)
  >>> dispatcher.index(elephant)
  >>> dispatcher.index(snake)

Modification and deletion.

  >>> rabbit.description = 'cute little creatures'
  >>> dispatcher.reindex(rabbit)
  >>> dispatcher.unindex(snake)

Flush queue.
  
  >>> dispatcher.flush()

Searching
---------

Now we can start querying the index.

  >>> from z3c.indexing.xapian.connection import ConnectionHub
  >>> hub = ConnectionHub('tmp.idx')

We should be able to find the "rabbit" item.
  
  >>> searcher = hub.get()
  >>> query = searcher.query_parse('rabbit')
  >>> len(searcher.search( query, 0, 30))
  1

Also by searching for the modified description.
  
  >>> searcher = hub.get()
  >>> query = searcher.query_parse('cute little creatures')
  >>> len(searcher.search( query, 0, 30))
  1

But the "snake" item shouldn't be there.

  >>> searcher = hub.get()
  >>> query = searcher.query_parse('snake')
  >>> len(searcher.search( query, 0, 30))
  0

Resolving
---------

  >>> from ZODB.tests.util import DB
  >>> db = DB()

Opened database and acquire root object:
  
  >>> conn = db.open()
  >>> root = conn.root()

Add these objects to the root object.
 
  >>> root['content'] = dict(rabbit=rabbit, elephant=elephant, snake=snake)

Commit transaction, so objects are added to the ZODB.

  >>> import transaction
  >>> transaction.commit()

Setup an intid service and an ``IKeyReference`` adapter that uses the
persistent object id to uniquely identify an object.

  >>> import zope.app.intid
  >>> component.provideUtility(zope.app.intid.IntIds(), zope.app.intid.interfaces.IIntIds)

  >>> import zope.app.keyreference.persistent
  >>> from persistent.interfaces import IPersistent
  >>> component.provideAdapter(
  ...    zope.app.keyreference.persistent.KeyReferenceToPersistent, (IPersistent,))
  
Register our content objects with the intid machinery.

  >>> from zope.app.container.contained import ObjectAddedEvent
  >>> zope.app.intid.addIntIdSubscriber(rabbit, ObjectAddedEvent(rabbit))
  >>> zope.app.intid.addIntIdSubscriber(elephant, ObjectAddedEvent(elephant))
  >>> zope.app.intid.addIntIdSubscriber(snake, ObjectAddedEvent(snake))

Provide the intid resolver as utility:

  >>> from z3c.indexing.xapian.resolver import IntIdResolver
  >>> component.provideUtility(IntIdResolver(), name='intid')

  >>> from zope.event import notify
  >>> from zope.app.container.contained import ObjectAddedEvent

Notify the intid framework that our content was added.
  
  >>> notify(ObjectAddedEvent(rabbit))
  >>> notify(ObjectAddedEvent(elephant))
  >>> notify(ObjectAddedEvent(snake))

Let's try out the resolver.

  >>> from z3c.indexing.xapian.interfaces import IResolver
  >>> resolver = component.getUtility(IResolver, name='intid')
  >>> id = resolver.getId(rabbit)
  >>> resolver.getObject(id) is rabbit
  True
  
Cleanup
-------

  >>> conn.close()
