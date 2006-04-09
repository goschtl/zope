##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""ZSCP Data Management

$Id$
"""
__docformat__ = "reStructuredText"

import persistent
import zope.interface

from zope.app.container.contained import Contained
from zf.zscp.interfaces import IZSCPRepository
from zf.zscp.repository import ZSCPRepository


class Repository(ZSCPRepository, persistent.Persistent, Contained):
    """A ZSCP-compliant repository as content type."""
    zope.interface.implements(IZSCPRepository)
