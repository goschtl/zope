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
"""

Revision information:
$Id: error.py,v 1.2 2002/12/25 14:13:02 jim Exp $
"""
from zope.interface import Interface

class IErrorReportingService(Interface):
    """Error Reporting Service Interface.
    """

    def raising(info, request=None):
        """Logs an exception.
        """

    def getProperties():
        """Gets the properties as dictionary.
           keep_entries, copy_to_logfile, ignored_exceptions
        """

    def setProperties(keep_entries, copy_to_zlog=0, ignored_exceptions=(),
                      RESPONSE=None):
        """Sets the properties. keep_entries, copy_to_logfile,
        ignored_exceptions
        """

    def getLogEntries():
        """Returns the entries in the log, most recent first.
        """

    def getLogEntryById(id):
        """Return LogEntry by ID
        """
