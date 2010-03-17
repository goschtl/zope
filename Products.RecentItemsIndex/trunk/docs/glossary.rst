Glossary
--------

.. glossary::

   date_name
        An attribute of a RecentItemsIndex.  The index uses this attribute's
        value as the name of an attribute of indexed documents which provides
        the "date" value for the document.  The index maintains documents in
        the index only while they are withing the :term:`max_length` most
        recent entries, either for the unclassified list or within a single
        classifier value.

   field_name
        An attribute of a RecentItemsIndex.  The index uses this attribute's
        value as the name of an attribute of indexed documents which provides
        a "classifier" for the document.  If the ``field_name`` attribute of
        the index is None, the index keeps only a single list of all indexed
        documents.

   guard_roles
        A list of one or more :term:`role` (s) that must be granted the
        :term:`guard_permission` in order for an object to be indexed.
        Ignored if no :term:`guard_permission` value is given.

   guard_permission
        The permission that must be granted to the :term:`guard_roles` for an
        object in order for it to be indexed. Ignored if no :term:`guard_roles`
        value is given.

   max_length
        An attribute of a RecentItemsIndex.  The index keeps only this many
        documents in either its unclassified list of documents or in the list
        for any single classifier value.

   permission
        A named "capability", protecting access to attributes and methods
        on objects.

   role
        Named :term:`permission` sets, such as ``Manager`` or ``Reviewer``.
        Roles represent a logical grouping of permissions which can be
        granted to users or groups.  The specific permissions granted to a
        role may vary from object to object, e.g. based on an item's workflow
        state.
