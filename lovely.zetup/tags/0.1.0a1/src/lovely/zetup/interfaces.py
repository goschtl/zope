##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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

from zope import interface


class IConfig(interface.Interface):
    pass


class IConfigurableSite(interface.Interface):
    """marker for configurable sites"""

class ISiteConfig(interface.Interface):

    config = interface.Attribute('Site configparser instance')


class INoZODBStarted(interface.Interface):
    """An event fired after the configuration is finished."""

    root = interface.Attribute('The zetup root object')


class NoZODBStarted(object):
    interface.implements(INoZODBStarted)

    def __init__(self, root):
        self.root = root

