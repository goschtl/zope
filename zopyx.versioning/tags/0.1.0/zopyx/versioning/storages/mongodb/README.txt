Database layout of the MongoDB storage
======================================

The MongoDB-backed version storage uses three collections:

metadata
--------

The ``metadata`` collections has a row for each versioned object. Each row
consists of the MongoDB internal ``_id`` field, the ``_oid`` field for storing the
object id of the versioned object and a counter ``_rev`` for counting the object
revisions (0...N).

revisions
---------

The ``revisions`` collections is used to store the versioned data. There is a
row for each revision of each versioned object. ``_oid`` and ``_rev`` are used
to identifying objects and their revisions. The ``_metadata`` holds metadata
about the revision itself. By default it contains only the ``created`` field
and an optional ``comment`` field. Additional revision specific metadata can be
added through the store() API method. The real data belong to a particular
revision is stored as ``_data`` field.

collections
-----------
This collection is used for versioning object collections. A versioned object
collection is described by the ``_oid`` and ``_rev`` of the collection itself
the list objects belong to the collection.  They are stored under
``collection_content`` as a sequence of embedded subobjects with fields
``_oid`` and ``_rev`` representing the state (given by its specific revision)
for each object of the collection.


