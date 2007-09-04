##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id: __init__.py 72084 2007-01-18 01:02:26Z rogerineichen $
"""
__docformat__ = 'restructuredtext'

from zope import interface
from zope.formlib import form
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.dublincore.interfaces import IZopeDublinCore
from z3c.reference.demo.interfaces import (IDemoFolder, IDemoImage)

from zope.traversing.browser.absoluteurl import absoluteURL
from zope.traversing.api import getPath

from zope import component
from zope.app.intid.interfaces import IIntIds
from zc import resourcelibrary

class DemoFolderEdit(form.EditForm):
    form_fields = form.Fields(IDemoFolder)
    label = u"Edit demofolder"
    

class DemoImageEdit(form.EditForm):
    form_fields = form.Fields(IDemoImage)


# temp
class Test(object):
    def test(self):
        intIds = component.getUtility(IIntIds)
        return intIds.getId(self.context)


# temp
class DemoPicker(object):
    
    def elements(self):
        return self.context.values()

    @property
    def url(self):
        return absoluteURL(self.context, self.request)


# test for dublin core metadata
class Meta(object):
    """Update dc title."""

    def edit(self):
        request = self.request
        dc = IZopeDublinCore(self.context)
        
        if 'dctitle' in request:
            dc.title = unicode(request['dctitle'])
        
        return {
            'dctitle': dc.title,
            }

    @property
    def url(self):
        return absoluteURL(self.context, self.request)
