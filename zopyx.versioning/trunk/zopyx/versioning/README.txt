zopyx.versioning
================

```zopyx.versioning`` is a generic versioning system for schema-oriented
content-objects (zope.schema, Archetypes, Dexterity etc.).


Basic concepts
--------------

- pluggable storage API (storing the versioned data)

- using JSON as data exchange format between objects to be versioned 
  and versioner and between versioner and backend storage (the storage
  may use a different serialization format (e.g. 'pickle' for a ZODB
  based backend or 'json' for a typical noSQL backend like MongoDB)

- making use of the Zope Component Architecture for adopting arbitrary 
  content objects to the storage API

- the solution does not claim to store and restore the complete state of
  an content object. Instead we focus on dealing with the metadata and
  the content itself. If an object uses a complex internal data model then it is
  in responsible to serialize and deserialize the data to JSON.


