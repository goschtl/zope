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
"""filtering view for ProcessInstances of a stateful workflow
 
$Id: content_filter.py,v 1.3 2004/03/14 02:17:09 srichter Exp $
"""
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.container.browser.contents import Contents
from zope.app.workflow.interfaces import IProcessInstanceContainerAdaptable
from zope.app.workflow.interfaces import IProcessInstanceContainer

__metaclass__ = type

class FilterList(Contents):

    __used_for__ = IProcessInstanceContainerAdaptable


    def filterByState(self, objList, state, workflow='default'):
        """Filter a list of objects according to given workflow and state

        objList  ... list of objects
        
        state    ... name of a state (of the given workflow) in which the
                     result objects must be

        workflow ... name of a workflow to which result objects must
                     be attached
        
        """
        res = []

        for obj in objList:
            adapter = IProcessInstanceContainer(obj['object'], None)
            if adapter:
                for item in adapter.values():
                    if item.processDefinitionName != workflow:
                        continue
                    if item.status == state:
                        res.append(obj)
                        break

        return res


    published_content = ViewPageTemplateFile('published_content.pt')

    # XXX: This method assumes you have a publishing workflow (SR) 
    def listPublishedItems(self):
        return self.filterByState(self.listContentInfo(), 'published')

