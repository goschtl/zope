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
$Id: FormView.py,v 1.3 2002/07/14 13:32:53 srichter Exp $
"""
from Zope.Publisher.Browser.BrowserView import BrowserView
from Interface import Interface
from Schema.IField import IField
from Zope.ComponentArchitecture import getView
import Schema

class FormView(BrowserView):
    def getWidgetsForSchema(self, schema, view_name):
        """Given a schema and a desired field name, get a list of
        widgets for it.
        """
        result = []
        for name in schema.names(1):
            attr = schema.getDescriptionFor(name)
            if IField.isImplementedBy(attr):
                widget = getView(attr, view_name, self.request)
                result.append(widget)
        return result

    def getFields(self):
        """XXX just a test method.
        """
        result = self.getWidgetsForSchema(ITestSchema, 'normal')
        print result
        return result
    
