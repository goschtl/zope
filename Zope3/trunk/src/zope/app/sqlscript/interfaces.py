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
$Id$
"""
import zope.schema
from zope.app import zapi
from zope.app.rdb.interfaces import ISQLCommand
from zope.component import getService, ComponentLookupError
from zope.app.i18n import ZopeMessageIDFactory as _

class MissingInput(Exception):
    pass

class ISQLScript(ISQLCommand):
    """A persistent script that can execute SQL."""

    connectionName = zope.schema.Choice(
        title=_(u"Connection Name"),
        description=_(u"The Connection Name for the connection to be used."),
        vocabulary="Connection Names",
        required=False)

    arguments = zope.schema.BytesLine(
        title=_(u"Arguments"),
        description=_(
        u"A set of attributes that can be used during the SQL command "
        u"rendering process to provide dynamic data."),
        required=False,
        default='',
        missing_value='')

    source = zope.schema.ASCII(
        title=_(u"Source"),
        description=_(u"The SQL command to be run."),
        required=False,
        default='',
        missing_value='')

    def getArguments():
        """Returns a set of arguments. Note that this is not a string!"""

    def getTemplate():
        """Get the SQL DTML Template object."""
   
