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
$Id: FSSync.py,v 1.2 2002/10/11 06:28:06 jim Exp $
"""

__metaclass__ = type

from Zope.App.FSSync.IObjectDirectory import IObjectDirectory
from Zope.App.FSSync.ObjectEntryAdapter import ObjectEntryAdapter

class ObjectDirectory(ObjectEntryAdapter):
    """Folder adapter to provide a file-system representation
    """

    __implements__ =  IObjectDirectory

    def contents(self):
        "See Zope.App.FSSync.IObjectDirectory.IObjectDirectory"
        return self.context.items()

__doc__ = ObjectEntryAdapter.__doc__ + __doc__

