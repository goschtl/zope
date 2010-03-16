Products.RecentItemsIndex
=========================

This product provides a ZCatalog index designed to optimize queries which
ask for the most recent objects that match a certain value for an attribute.
The designed usage is a query for the most recent objects of a particular
portal type.

The index only retains up to a fixed number of items for each field 
value which means that the performance of queries using the index
are independant of the size of the catalog.

The index also has a custom query interface so that applications
may query it directly for greatest efficiency since it handles both
the result selection and sorting simultaneously.

At the moment the index is not searchable through the standard ZCatalog
``searchResults()`` API. This is because the catalog does not yet support
indexes that can do searching and sorting simultaneously as this one
does.

Contents:

.. toctree::
   :maxdepth: 2

   CHANGES

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

