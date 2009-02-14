##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""FTP-specific interfaces

$Id: browser.py 96546 2009-02-14 20:48:37Z shane $
"""

from zope.publisher.interfaces.base import IPublishTraverse
from zope.publisher.interfaces.base import IRequest

class IFTPRequest(IRequest):
    """FTP Request
    """

class IFTPPublisher(IPublishTraverse):
    """FTP-specific traversal"""
