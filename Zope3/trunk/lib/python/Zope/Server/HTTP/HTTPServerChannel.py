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

$Id: HTTPServerChannel.py,v 1.2 2002/06/10 23:29:35 jim Exp $
"""

from Zope.Server.ServerChannelBase import ServerChannelBase
from HTTPTask import HTTPTask
from HTTPRequestParser import HTTPRequestParser


class HTTPServerChannel(ServerChannelBase):
    """HTTP-specific Server Channel"""

    __implements__ = ServerChannelBase.__implements__

    task_class = HTTPTask
    parser_class = HTTPRequestParser
