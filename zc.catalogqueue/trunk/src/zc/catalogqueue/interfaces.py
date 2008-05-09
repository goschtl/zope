##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import zope.interface

class ICatalogQueue(zope.interface.Interface):

    def add(id):
        """Add the object with the given id to the catalog
        """

    def update(id):
        """Update the object with the given id in the catalog
        """

    def remove(id):
        """Remove the object with the given id in the catalog
        """

    def process(ids, catalogs, limit):
        """Process up to limit objects, returning the number processed

        The first argument is an object with a getObject(id) method.

        Catalogs is a multi-iterable collection of
        zope.index.interfaces.IInjection objects to be updated.
        """

    def __len__():
        """Return the number of unprocessed cataloging events."""

    # We're not using zope.schema in order to keep dependencies to a minimum.

    lastProcessedTime = zope.interface.Attribute(
        """Time the queue was last processed.

        This represents the time when the last successful call to `process()`
        returned.  If this is ``None``, the queue has not been processed since
        this field was added.  This may simply mean that the queue was last
        processed before the implementation supported tracking this.

        """)

    totalProcessed = zope.interface.Attribute(
        """Number of cataloging events processed.

        A value of 0 may be caused by the last processing having happened
        before this information was tracked.  If ``lastProcessedTime`` is set,
        this value may be considered valid, even if 0.

        """)
