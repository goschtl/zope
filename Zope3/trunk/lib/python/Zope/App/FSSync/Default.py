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
$Id: Default.py,v 1.2 2002/10/11 06:28:05 jim Exp $
"""

__metaclass__ = type

from Zope.App.FSSync.ObjectEntryAdapter import ObjectEntryAdapter
from Zope.App.FSSync.IObjectFile import IObjectFile
from Zope.XMLPickle.XMLPickle import dumps


class Default(ObjectEntryAdapter):
    """Default File-system representation for objects
    """

    __implements__ =  IObjectFile

    def getBody(self):
        "See Zope.App.FSSync.IObjectFile.IObjectFile"
        if type(self.context) is str:
            return self.context
        return dumps(self.context)

    def setBody(self, body):
        pass
    
    def factory(self):
        "See Zope.App.FSSync.IObjectEntry.IObjectEntry"
        # We have no factory, cause we're a pickle.


__doc__ = Default.__doc__ + __doc__

