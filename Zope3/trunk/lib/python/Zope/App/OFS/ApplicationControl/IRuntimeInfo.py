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
__doc__ = """ Runtime Information Interface

$Id: IRuntimeInfo.py,v 1.2 2002/06/10 23:27:51 jim Exp $"""

from Interface import Interface

class IRuntimeInfo(Interface):
    """ Runtime Information Adapter for Application Control """

    def getZopeVersion():
        """Return a string containing the descriptive version of the
           current zope installation"""

    def getPythonVersion():
        """Return a string containing verbose description of the python
           interpreter"""
    
    def getPythonPath():
        """Return a tuple containing the lookup paths of the python interpreter
        """

    def getSystemPlatform():
        """Return the system platform name in a 5 tuple of
           (sysname, nodename, release, version, machine)"""

    def getCommandLine():
        """Return the command line string Zope was invoked with"""

    def getProcessId():
        """Return the process id number currently serving the request
        """

    def getUptime():
        """Return a string containing the Zope server uptime in unix uptime
           format with seconds ([NN days, ]HH:MM:SS)"""

