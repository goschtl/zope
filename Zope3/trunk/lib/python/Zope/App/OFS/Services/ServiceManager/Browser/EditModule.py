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
"""Handle form to edit module

$Id: EditModule.py,v 1.2 2002/11/30 18:39:17 jim Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Services.ServiceManager.Module import Manager

class EditModule(BrowserView):

    def update(self):
        if "source" in self.request:
            self.context.update(self.request["source"])
            return u"The source was updated."
        else:
            return u""
