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
$Id: sql.py,v 1.8 2003/09/21 17:31:56 jim Exp $
"""
import zope.schema

from zope.app.interfaces.rdb import ISQLCommand
from zope.component import getService, ComponentLookupError
from zope.app.i18n import ZopeMessageIDFactory as _

class MissingInput(Exception):
    pass

class SQLConnectionName(zope.schema.TextLine):
    """SQL Connection Name"""

    def __allowed(self):
        """Note that this method works only if the Field is context wrapped."""
        try:
            connection_service = getService(self.context,
                                            "SQLDatabaseConnections")
        except ComponentLookupError:
            return []

        return connection_service.getAvailableConnections()

    allowed_values = property(__allowed)

class ISQLScript(ISQLCommand):
    """A persistent script that can execute SQL."""

    connectionName = SQLConnectionName(
        title=_(u"Connection Name"),
        description=_(u"The Connection Name for the connection to be used."),
        required=False)

    arguments = zope.schema.BytesLine(
        title=_(u"Arguments"),
        description=_(u"A set of attributes that can be used during the SQL command "
                      u"rendering process to provide dynamic data."),
        required=False)

    source = zope.schema.Bytes(
        title=_(u"Source"),
        description=_(u"The SQL command to be run."),
        required=True)

    def getArguments():
        """Returns a set of arguments. Note that this is not a string!"""

    def getTemplate():
        """Get the SQL DTML Template object."""
