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
$Id: SSQLScript.py,v 1.1 2002/07/19 13:12:32 srichter Exp $
"""
import Schema
from Zope.ComponentArchitecture import getService
from Zope.App.Traversing import getParent
from Zope.ContextWrapper import ContextMethod

class SQLArguments(Schema.Str):
    """Arguments"""


class SQLConnectionName(Schema.Str):
    """SQL Connection Name"""

    def items(self):
        """Note that this method works only if the Field is context wrapped."""
        connection_service = getService(self, "Connections")
        connections = connection_service.getAvailableConnections()
        return connections

    items = ContextMethod(items)


class SSQLScript(Schema.Schema):

    connectionName = SQLConnectionName(
        id="connectionName",
        title="Connection Name",
        description="""The Connection Name for the connection to be used.""",
        required=1)

    arguments = SQLArguments(
        id="arguments",
        title="Arguments",
        description='A set of attributes that can be used during the DTML '
                    'rendering process to provide dynamic data.',
        required=1)

    source = Schema.Str(
        id="source",
        title="Source",
        description="""The source od the page template.""",
        required=1)

