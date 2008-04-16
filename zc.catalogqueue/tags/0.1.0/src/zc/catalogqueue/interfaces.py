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
        
