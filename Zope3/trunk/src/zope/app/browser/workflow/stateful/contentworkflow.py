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
 
$Id: contentworkflow.py,v 1.1 2003/05/08 17:27:17 jack-e Exp $
"""
__metaclass__ = type
 
from zope.component import getServiceManager
from zope.publisher.browser import BrowserView
from zope.app.form.utility import setUpWidgets, getWidgetsDataForContent
from zope.app.interfaces.workflow.stateful import IContentWorkflowsUtility

class ContentWorkflowsUtilityView(BrowserView):
 
    def getName(self):
        return """I'm a ContentWorkflows Utility"""



