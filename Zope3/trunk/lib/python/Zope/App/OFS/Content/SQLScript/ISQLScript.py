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
$Id: ISQLScript.py,v 1.7 2002/09/05 18:55:02 jim Exp $
"""
from Zope.App.RDB.ISQLCommand import ISQLCommand
from Interface.Attribute import Attribute
from Zope.ComponentArchitecture import getService
from Zope.ContextWrapper import ContextMethod
import Zope.Schema

class SQLConnectionName(Zope.Schema.Str):
    """SQL Connection Name"""

    def items(self):
        """Note that this method works only if the Field is context wrapped."""
        connection_service = getService(self, "Connections")
        connections = connection_service.getAvailableConnections()
        return connections

    items = ContextMethod(items)

class ISQLScript(ISQLCommand):
    """A persistent script that can execute SQL."""

    connectionName = SQLConnectionName(
        title="Connection Name",
        description="The Connection Name for the connection to be used.",
        required=1)

    arguments = Zope.Schema.Str(
        title="Arguments",
        description="A set of attributes that can be used during the DTML "
                    "rendering process to provide dynamic data.",
        required=0)

    source = Zope.Schema.Str(
        title="Source",
        description="The source of the page template.",
        required=1)

    maxCache = Zope.Schema.Int(
        title="Maximum results to cache",
        description="The size of the SQL script cache.",
        min=0,
        required=1)

    cacheTime = Zope.Schema.Int(
        title="Maximum time (sec) to cache",
        description="The time in seconds that results are cached. "
                    "Setting to zero disables caching.",
        min=0,
        required=1)

    def setArguments(arguments):
        """Processes the arguments (which could be a dict, string or whatever)
        to arguments as they are needed for the rendering process."""

    def getArguments():
        """Get the arguments. A method is preferred here, since some argument
        evaluation might be done."""

    def getArgumentsString():
        """This method returns the arguments string."""

    def setSource(source):
        """Save the source of the page template."""

    def getSource():
        """Get the source of the page template."""

    def getTemplate():
        """Get the SQL DTML Template object."""

    def setConnectionName(name):
        """Save the connection name for this SQL Script."""

    def getConnectionName():
        """Get the connection name for this SQL Script."""

    def setMaxCache(maxCache):
        """Set the size of the SQL script cache."""

    def getMaxCache():
        """Get the size of the SQL script cache."""

    def setCacheTime(cacheTime):
        """Set the time in seconds that results are cached."""

    def getCacheTime():
        """Get the time in seconds that results are cached."""
