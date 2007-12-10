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

__docformat__ = "reStructuredText"


import persistent

_marker = object()
class Persistent(persistent.Persistent):

    def __setattr__(self, name, value):
        if getattr(self, name, _marker) != value:
            # only set the value if changed
            super(Persistent, self).__setattr__(name, value)


    def __delattr__(self, name):
        if name in self.__dict__:
            # only delete if in dict
            persistent.Persistent.__delattr__(self, name)


