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
$Id: SchemaTestObject.py,v 1.2 2002/07/16 23:42:59 srichter Exp $
"""
import Schema

from Zope.Publisher.HTTP.tests.TestRequest import TestRequest
from Zope.Publisher.Browser.IBrowserView import IBrowserView
from Zope.App.PageTemplate import ViewPageTemplateFile

from Zope.App.Forms.Views.Browser import Widget
from Zope.App.Forms.Widget import CustomWidget
from Zope.App.Forms.Views.Browser.FormView import FormView


class TestBrowserRequest(TestRequest):
    """Since we have IBrowserViews, we need a request that works
    for IBrowserView."""
    def __init__(self, form):
        super(TestBrowserRequest, self).__init__()
        self.form = form

    def getPresentationType(self):
        return IBrowserView


class Email(Schema.Str):
    """A simple customized field."""
    pass


class STestObject(Schema.Schema):
    """A simple Schema."""

    id = Schema.Str(
        id="id",
        title="Id",
        required=1)
    
    title = Schema.Str(
        id="title",
        title="Title",
        required=0)
    
    data = Schema.Str(
        id="data",
        title="Data",
        description="Data stored by the object",
        required=0)
    
    creator = Email(
        id="creator",
        title="Creator",
        description="Email of the creator of the content object",
        default="foo@bar.com",
        required=1)
    
    
class TestObject(object):
    """A very simple content object."""
    __implements__ = STestObject

    def __init__(self, id, title, creator, data=None):
        self.id = id
        self.title = title
        self.creator = creator
        self.data = data


class Edit(FormView):
    """A simple Edit View"""
    form = ViewPageTemplateFile('testEditForm.pt')
    custom_widgets = {'creator': CustomWidget(Widget.TextWidget,
                                              displayWidth=30),
                      'data': CustomWidget(Widget.FileWidget)}


def EditFactory(context=None, request=None):

    if request is None:
        request = TestBrowserRequest({})

    object = TestObject(id=1, title="Test", creator="srichter@cbu.edu",
                        data="Some data")
    return Edit(object, request)
