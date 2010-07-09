zopyx.versioning
================

``zopyx.versioning`` is a generic versioning system for schema-oriented
content-objects (zope.schema, Archetypes, Dexterity etc.).

Why another versioning system?
------------------------------

Existing versioning approaches in the Zope world are:

CMFEditions
++++++++++++

- widely used
- very monolithic
- too tight integration with CMF
- fragile implementation
- doing "too much"
- doing "too much" in a very intransparent way
- no backend serialization format other than Python pickles
- only ZODB-based backend
- backend not pluggable

Basic concepts
--------------

- golden rule #1: keep it simple, keep it small

- pluggable storage API (storing the versioned data)

- using JSON as data exchange format between objects to be versioned 
  and versioner and between versioner and backend storage (the storage
  may use a different serialization format (e.g. 'pickle' for a ZODB
  based backend or 'json' for a typical noSQL backend like MongoDB)

- making use of the Zope Component Architecture for adopting arbitrary 
  content objects to the storage API

- the solution does not claim to store and restore the complete state of
  an content object. Instead we focus on dealing with the metadata and
  the content itself. If an object uses a complex internal data model then it
  is in responsible to serialize and deserialize the data to JSON.

- leave complex functionality (likely handling of references, object relations
  etc.) out of the core versioning engine - this might be handled through
  adapters implementing IVersionSupport.


Open points
-----------

- should de-duplication be handled on the storage layer or the versioning layer
  (I assume on the storage layer as an optional feature in order to keep the
  overall complexity low)

- all versionable objects must provide a unique ID (``UID`` for
  Archetypes-backed content). How about Dexterity? How about
  ZTK/zope.schema-based content?

- how deal with "large" content. E.g. a MongoDB-based backend has by default
  a 4MB limit for embedded documents (usually enough for standard content but
  not for binary content like images)   

Author
------

| ZOPYX Ltd.
| c/o Andreas Jung
| Charlottenstr. 37/1
| D-72070 Tuebingen
| Germany
| info@zopyx.com
| www.zopyx.com
