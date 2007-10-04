##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Browser code for JS button demo.

$Id: layer.py 75942 2007-05-24 14:53:46Z srichter $
"""
__docformat__="restructuredtext"
from zope.security.proxy import removeSecurityProxy
from zope.viewlet.viewlet import CSSViewlet

from z3c.formjsdemo.chat.interfaces import IChatRoom
from z3c.formjsdemo.tree.interfaces import ITreeNode

IndexCSSViewlet = CSSViewlet('index.css')


class IndexView(object):
    """A simple index view for the demos."""

    def chatRooms(self):
        return filter(IChatRoom.providedBy,
                      removeSecurityProxy(self.context).values())

    def treeNodes(self):
        return filter(ITreeNode.providedBy,
                      removeSecurityProxy(self.context).values())
