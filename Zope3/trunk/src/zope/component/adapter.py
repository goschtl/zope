##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""adapter service
"""

__metaclass__ = type
import sys
from zope.interface import implements
from zope.interface.adapter import AdapterRegistry
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IAdapterService
from zope.component.service import GlobalService
import warnings

class IGlobalAdapterService(IAdapterService):

    def provideAdapter(required, provided, factories, name='', with=()):
        """Provide an adapter

        An adapter provides an interface for objects that have another
        interface.

        XXX: Arguments must be updated.
        Arguments:

        forInterface -- The interface the adapter provides an interface for.

        providedInterface -- The provided interface

        maker -- a sequence of factories that are used to create the adapter.
        The first factory is called with the object to be adapted, subsequent
        factories are called with the results of the previous factory.
        """

    def getRegisteredMatching(required=None,
                              provided=None,
                              name=None,
                              with=None):
        """Return information about registered data

        A five-tuple is returned containing:

          - registered name,

          - registered for interface

          - registered provided interface, and

          - registered data
        """

class GlobalAdapterService(AdapterRegistry, GlobalService):

    implements(IGlobalAdapterService)

