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
$Id: IErrorReportingService.py,v 1.4 2002/10/23 16:00:19 jim Exp $
"""
from Interface import Interface

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

    def setProperties(keep_entries, copy_to_zlog=0, ignored_exceptions=(), RESPONSE=None):
        """Sets the properties. keep_entries, copy_to_logfile, ignored_exceptions
        """

    def getLogEntries():
        """Returns the entries in the log, most recent first.
        """

    def getLogEntryById(id):
         """Return LogEntry by ID
         """
