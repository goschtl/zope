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

$Id: query.py,v 1.3 2002/12/30 18:43:08 stevea Exp $
"""

from zope.interface import Interface, Attribute
from zope.app.security.permission import PermissionField
from zope.app.interfaces.services.configuration \
    import INamedConfigurationInfo, INamedConfiguration
from zope.app.component.interfacefield import InterfacesField

class IQueryProcessor(Interface):

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

        (query_id, permission_id, input_interface, output_interface)'''

    def processQuery(query_id, input):
        '''Processes the input, using the query registered with query_id.

        The input must be adaptable to the input interfaces registered for
        the query_id.'''

class IQueryConfigurationInfo(INamedConfigurationInfo):

    permission = PermissionField(title=u'Required permission')
    inputInterfaces = InterfacesField(title=u'Input interfaces')
    outputInterfaces = InterfacesField(title=u'Output interfaces')

class IQueryConfiguration(IQueryConfigurationInfo, INamedConfiguration):

    pass

