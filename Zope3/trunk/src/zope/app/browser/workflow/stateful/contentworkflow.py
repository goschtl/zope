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
"""ContentWorkflow Utility views
 
$Id: contentworkflow.py,v 1.2 2003/06/03 22:46:18 jim Exp $
"""
__metaclass__ = type
 
from zope.publisher.browser import BrowserView

class ContentWorkflowsUtilityView(BrowserView):
 
    def getName(self):
        return """I'm a ContentWorkflows Utility"""



