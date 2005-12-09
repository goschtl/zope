##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""default VersionControl view classes

$Id$
"""

from versioning import interfaces

from zope.app import zapi
from zope.security.proxy import removeSecurityProxy



class VersionControlView(object):
    """displays version data of an object"""

    __used_for__ = interfaces.IVersioned

    def __init__(self, context, request):
        self.context = context
        self.request = request
        history = zapi.getUtility(interfaces.IHistoryStorage)
        self.rep = interfaces.ICopyModifyMergeRepository(history)
        
    def listVersions(self):
        #import pdb; pdb.set_trace()
        versions = self.rep.listVersions(removeSecurityProxy(self.context))
        return [x for x in versions]
    
    def saveVersion(self):
        self.rep.saveAsVersion(removeSecurityProxy(self.context))
        self.request.response.redirect("VersionControlInfo.html")

        
    






