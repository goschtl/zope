##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: ObjectEntryAdapter.py,v 1.2 2002/10/11 06:28:05 jim Exp $
"""

__metaclass__ = type

class ObjectEntryAdapter:
    """Convenience Base class for ObjectEntry adapter implementations
    """

    def __init__(self, context):
        self.context = context

    def extra(self):
        "See Zope.App.FSSync.IObjectEntry.IObjectEntry"

    def typeIdentifier(self):
        "See Zope.App.FSSync.IObjectEntry.IObjectEntry"
        class_ = self.context.__class__
        return "%s.%s" % (class_.__module__, class_.__name__)

    def factory(self):
        "See Zope.App.FSSync.IObjectEntry.IObjectEntry"
        # Return the dotted class name, assuming that it can be used
        class_ = self.context.__class__
        return "%s.%s" % (class_.__module__, class_.__name__)
    

__doc__ = ObjectEntryAdapter.__doc__ + __doc__

