##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
$Id: SQLScriptEdit.py,v 1.4 2002/07/19 13:12:33 srichter Exp $
"""
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.App.Forms.Views.Browser import Widget 
from Zope.App.Forms.Widget import CustomWidget 
from Zope.App.Forms.Views.Browser.FormView import FormView

class SQLScriptEdit(FormView):
    form = ViewPageTemplateFile('edit.pt')
    custom_widgets = {'connectionName': CustomWidget(Widget.ListWidget,
                                                     size=1),
                      'arguments': CustomWidget(Widget.TextAreaWidget,
                                                height=3, width=40),
                      'source': CustomWidget(Widget.TextAreaWidget,
                                             height=10, width=80)}
    fields_order = ('connectionName', 'arguments', 'source')

    def getAllConnections(self):
        parent = getParent(self.context)
        connection_service = getService(parent, "Connections")
        connections = connection_service.getAvailableConnections()
        return connections
