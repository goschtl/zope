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

$Id: IDispatcherLogging.py,v 1.2 2002/06/10 23:29:34 jim Exp $
"""

from Interface import Interface


class IDispatcherLogging(Interface):
    """This interface provides methods through which the Dispatcher will
       write its logs. A distinction is made between hit and message logging,
       since they often go to different output types and can have very
       different structure.
    """

    def log (message):
        """Logs general requests made to the server.
        """

    def log_info(message, type='info'):
        """Logs informational messages, warnings and errors.
        """
