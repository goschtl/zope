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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: IQueryService.py,v 1.1 2002/12/05 14:33:36 stevea Exp $
"""
from Interface import Interface

class IQueryService(Interface):

    def listQueries():
        '''Returns a list of query registrations.

        (query_id, permission_id, input_interface, output_interface)'''

    def processQuery(query_id, input):
        '''Processes the input, using the query registered with query_id.

        The input is adapted to the input interface of the query processor
        that is registered for the query_id.'''

