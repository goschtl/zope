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
$Id: ISQLScript.py,v 1.2 2002/07/19 13:12:32 srichter Exp $
"""
from Zope.App.RDB.ISQLCommand import ISQLCommand
from Interface.Attribute import Attribute

class ISQLScript(ISQLCommand):
    """A persistent script that can execute SQL."""

    arguments = Attribute('''A set of attributes that can be used during
                             the DTML rendering process to provide dynamic
                             data.''')

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
