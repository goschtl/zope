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

$Id: IServer.py,v 1.2 2002/06/10 23:29:34 jim Exp $
"""

from Interface import Interface
from Interface.Attribute import Attribute


class IServer(Interface):
    """This interface describes the basic base server.

       The most unusual part about the Zope servers (since they all
       implement this interface or inherit its base class) is that it
       uses a mix of asynchronous and thread-based mechanism to
       serve. While the low-level socket listener uses async, the
       actual request is executed in a thread.  This has the huge
       advantage that if a request takes really long to process, the
       server does not hang at that point to wait for the request to
       finish.
    """

    channel_class = Attribute("""
                        The channel class defines the type of channel
                        to be used by the server. See IServerChannel
                        for more information.
                              """)

    SERVER_IDENT = Attribute("""
                        This string identifies the server. By default
                        this is 'Zope.Server.' and should be
                        overridden.
                        """)

