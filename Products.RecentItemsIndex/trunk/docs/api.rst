The RecentItemsIndex API
========================

Constructing a RecentItemsIndex in Python
-----------------------------------------

The constructor's signature is:

.. code-block:: python

    def __init__(self,
                 id,
                 field_name=None,
                 date_name=None,
                 max_length=None,
                 guard_roles=None,
                 guard_permission=None,
                 extra=None,
                 caller=None,
                ):
        """ Recent items index constructor

        id -- Zope id for index inside its catalog.

        field_name -- Name of attribute used to classify the objects. A
        recent item list is created for each value of this field indexed.
        If this value is omitted, then a single recent item list for all
        cataloged objects is created.

        date_name -- Name of attribute containing a date which specifies the
        object's age.

        max_length -- Maximum length of each recent items list.

        guard_roles -- A list of one or more roles that must be granted the
        guard permission in order for an object to be indexed. Ignored if
        no guard_permission value is given.

        guard_permission -- The permission that must be granted to the
        guard roles for an object in order for it to be indexed. Ignored if
        no guard_roles value is given.
        """

Constructing a RecentItemsIndex in the ZMI
------------------------------------------

For compatibility with the ZCatalog's index factory page, the constructor
allows several values to be passed as attributes of the ``extra`` argument:

- :term:`field_name`

- :term:`date_name`

- :term:`max_length`

- :term:`guard_roles`

- :term:`guard_permission`

The catalog transfers these values from the form,  submitted when adding
the index to the catalog, to the object passed as the ``extras`` argument.

The ``caller`` argument is ignored, even if passed from the ZMI.


Interfaces
----------

:class:`RecentItemsIndex` implements three standard Zope2 index interfaces,
defined in :mod:`Products.PluginIndexes.interfaces`:

- :class:`~Products.PluginIndexes.interfaces.IPluggableIndex`

- :class:`~Products.PluginIndexes.interfaces.IUniqueValueIndex`

- :class:`~Products.PluginIndexes.interfaces.ISortIndex`

:class:`RecentItemsIndex` implements a custom index interfaces,
defined in :mod:`Products.RecentItemsIndex.interfaces`:

- :class:`~Products.RecentItemsIndex.interfaces.IRecentItemsIndex`

The :class:`IPluggableIndex` API
################################

This interface declares the base functionality for any index used within
a Zope2 ZCatalog.

.. code-block:: python

 class IPluggableIndex(Interface):

     def getId():
         """ Return the id of index.
         """

     def getEntryForObject(documentId, default=None):
         """ Return a mapping of information known to the index for a document.
         """

In the case of the RecentItemsIndex, this mapping contains two keys:
``value`` holds the value for the document of the attribute named by the
:term:`field_name` of the index, and ``date`` holds the value for the doucment
of the attribute named by the :term:`date_name` of the index.  The index
returns results from queries sorted in descending date order.

.. code-block:: python

     def getIndexSourceNames():
         """Get a sequence of attribute names that are indexed by the index.
         """

In the case of the RecentItemsIndex, this method returns a one-tuple holding
the value of the :term:`field_name` attribute, which may be None if the index
was defined without any classification attribute.

.. code-block:: python

     def index_object(documentId, obj, threshold=None):
         """Index an object.

         'documentId' is the integer ID which identifies the document
         uniquely within the catalog.

         'obj' is the object to be indexed.

         'threshold' is the number of words to process between committing
         subtransactions.  If None, subtransactions are disabled.
         """

In the case of the RecentItemsIndex, this method ignores the ``threshold``
argument.  Indexes which have a :term:`field_name` attribute defined use the
value of that attribute as the name of an attribute to fetch from the
document:  in this case all documents which have the same value for that
attribute are grouped together in a list.  Indexes which do not have a 
:term:`field_name` attribute defined store all documents in a single list.
Only the :term:`max_length` most recent documents are kept in any list,
based on the value of the document attribute named by the :term:`date_name`
attribute of the index.

.. code-block:: python

     def unindex_object(documentId):
         """Remove the documentId from the index."""

     def _apply_index(request):
         """Apply the index to query parameters given in 'request'.

         The argument should be a mapping object.

         If the request does not contain the needed parameters, then
         None is returned.

         If the request contains a parameter with the name of the column
         + "_usage", it is sniffed for information on how to handle applying
         the index. (Note: this style or parameters is deprecated)

         If the request contains a parameter with the name of the
         column and this parameter is either a Record or a class
         instance then it is assumed that the parameters of this index
         are passed as attribute (Note: this is the recommended way to
         pass parameters since Zope 2.4)

         Otherwise two objects are returned.  The first object is a
         ResultSet containing the record numbers of the matching
         records.  The second object is a tuple containing the names of
         all data fields used.
         """

At the moment, the RecentItemsIndex does not participate in the standard
ZCatalog search interface, which this method serves.  It therefore always
returns ``None``.

.. code-block:: python

     def numObjects():
         """ Return the number of indexed objects.
         """

     def indexSize():
         """ Return the size of the index in terms of distinct values.
         """

     def clear():
         """ Empty the index.
         """


The :class:`IUniqueValueIndex` API
##################################

.. code-block:: python

 class IUniqueValueIndex(IPluggableIndex):
     """ An index which can return lists of unique values contained in it
     """
     def hasUniqueValuesFor(name):
         """ Return true if the index can return the unique values for name
         """

The RecentItemsIndex returns values only if ``name`` matches its
:term:`field_name`.

.. code-block:: python

     def uniqueValues(name=None, withLengths=0):
         """Return the unique values for name.

         If 'withLengths' is true, returns a sequence of tuples of
         (value, length).
         """

The RecentItemsIndex returns values only if ``name`` matches its
:term:`field_name`, or if ``name`` is None.


The :class:`ISortIndex` API
###########################

.. code-block:: python

 class ISortIndex(IPluggableIndex):
     """ An index which may be used to sort a set of document ids.
     """
     def keyForDocument(documentId):
         """Return the sort key that cooresponds to the specified document id.

         This method is no longer used by ZCatalog, but is left for backwards
         compatibility.
         """

     def documentToKeyMap():
         """ Return a mappingused to look up the sort key for a document id.
         """


The :class:`IRecentItemsIndex` API
##################################

.. code-block:: python

 class IRecentItemsIndex(IUniqueValueIndex, ISortIndex):
     """ API for index returning only "recent" items of a given type.
     """
     def getItemCounts():
         """ Return a mapping of field values => item counts.
         """

     def query(value=None, limit=None, merge=1):
         """ Return a lazy sequence of catalog brains like a catalog search.

         Return results in order, newest first, for the value(s) given.

         If 'value' is omitted, return the most recent for all values.
         
         'limit', if passed, must be an integer value restricting the maximum
         number of results.
         
         If no limit is specified, use the 'max_length' of the index as
         the limit.

         'merge' is a flag:  if true, return a lazy map of the brains.  If
         false, return a sequence of (value, rid, fetch) tuples which can
         be merged later.
         """
