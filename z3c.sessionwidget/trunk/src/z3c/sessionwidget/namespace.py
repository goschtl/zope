##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Session Namespace

$Id$
"""
__docformat__ = "reStructuredText"
from zope.app.session.interfaces import ISession
from z3c.sessionwidget import widget

class sessionNamespace(object):
    """Used to traverse to a session."""

    def __init__(self, ob, request=None):
        self.context = ob
        self.request = request

    def traverse(self, name, ignore):
        return ISession(self.request)[name]
