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
"""

$Id: query.py,v 1.7 2003/02/06 13:03:39 stevea Exp $
"""

from zope.interface import Interface, Attribute
from zope.app.security.permission import PermissionField
from zope.app.interfaces.services.configuration import INamedConfigurationInfo
from zope.app.interfaces.services.configuration import INamedConfiguration
from zope.app.component.interfacefield import InterfacesField
from zope.schema.interfaces import ITuple
# There's another import further down

class IQueryProcessorsField(ITuple):
    """Field for entering a pipeline of query processors."""

class IQueryProcessable(Interface):
    """Marker interface that says that the implementing component is adaptable
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

class IQueryService(Interface):

    def listQueries():
        '''Returns a list of query registrations.

        Each element of the list is an IQueryListItem.'''

    def processQuery(query_id, input):
        '''Processes the input, using the query registered with query_id.

        The input must be adaptable to the input interfaces registered for
        the query_id.'''

class IQueryListItem(Interface):

    id = Attribute('The id of this query.')
    #permission = Attribute('Permission required to run the query.'
    #                       ' An object, not an id.')
    #inputInterfaces = Attribute('Sequence of interfaces the input must be'
    #                            ' adaptable to.')
    #outputInterfaces = Attribute('Sequence of interfaces the output must be'
    #                             ' adaptable to.')
    permission = PermissionField(title=u'Required permission', required=False)

    inputInterfaces = InterfacesField(title=u'Input interfaces',
                                      basetype=None)
    outputInterfaces = InterfacesField(title=u'Output interfaces',
                                       basetype=None)

# The import is here to avoid circular imports
from zope.app.services.queryfield import QueryProcessorsField

class IQueryConfigurationInfo(INamedConfigurationInfo):

    permission = PermissionField(title=u'Required permission', required=False)
    inputInterfaces = InterfacesField(title=u'Input interfaces',
                                      basetype=None)
    outputInterfaces = InterfacesField(title=u'Output interfaces',
                                       basetype=None)
    processors = QueryProcessorsField(title=u'Query processors',
                                      required=False)

class IQueryConfiguration(IQueryConfigurationInfo, INamedConfiguration):

    def getProcessors():
        'Returns a sequence of query processor objects.'

