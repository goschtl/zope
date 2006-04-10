##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.app.i18n import ZopeMessageFactory as _
from zope.interface import implements

from zope.generic.component import IInterfaceKeyDescription



class InterfaceKeyDescription(object):
    """Information description."""

    implements(IInterfaceKeyDescription)

    def __init__(self, interface, label=None, hint=None):
        self.interface = interface

        if label is None:
            self.label = _(interface.__name__)
        else:
            self.label = label

        if hint is None:
            self.hint = _(interface.__doc__)
        else:
            self.hint = hint
