##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Query framework definitions and support interfaces

$Id: query.py,v 1.12 2004/03/09 17:11:55 jim Exp $
"""

from zope.interface import Interface, Attribute
from zope.schema.interfaces import ITuple
# There's another import further down

class IQueryProcessorsField(ITuple):
    """Field for entering a pipeline of query processors."""

class IQueryProcessable(Interface):
    """Query Processor

    Marker interface that says that the implementing component is adaptable
    to IQueryProcessor, although maybe only via a named adapter."""

class IQueryProcessor(IQueryProcessable):

    inputInterfaces = Attribute("Sequence of input interfaces")
    outputInterfaces = Attribute("Sequence of output interfaces")

    def __call__(query):
        """Processes the query returning the result.

           The query must be adaptable to each interface in input_interface.
           The output should be adaptable to each interface in the
           output_interface.
        """

# The import is here to avoid circular imports
from zope.app.services.queryfield import QueryProcessorsField
