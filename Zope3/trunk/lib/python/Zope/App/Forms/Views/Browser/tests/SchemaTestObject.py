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
$Id: SchemaTestObject.py,v 1.9 2002/09/07 16:18:48 jim Exp $
"""
from Interface import Interface
import Zope.Schema
from Zope.App.Forms.Converter import StrToIntConverter

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


class Email(Zope.Schema.Bytes):
    """A simple customized field."""
    pass


class ITestObject(Interface):
    """A simple Schema."""

    id = Zope.Schema.Int(
        title="Id",
        required=1)
    
    title = Zope.Schema.Bytes(
        title="Title",
        required=0)
    
    data = Zope.Schema.Bytes(
        title="Data",
        description="Data stored by the object",
        required=0)
    
    creator = Email(
        title="Creator",
        description="Email of the creator of the content object",
        default="foo@bar.com",
        required=1)
    
    
class TestObject(object):
    """A very simple content object."""
    __implements__ = ITestObject

    def __init__(self, id, title, creator, data=None):
        self.id = id
        self.title = title
        self.creator = creator
        self.data = data


class Edit(FormView):
    """A simple Edit View"""
    form = ViewPageTemplateFile('testEditForm.pt')
    schema = ITestObject
    custom_widgets = {'id': Widget.IntWidget,
                      'creator': CustomWidget(Widget.TextWidget,
                                              displayWidth=30),
                      'data': CustomWidget(Widget.FileWidget)}
    fields_order = ('id', 'title', 'creator', 'data')


def EditFactory(context=None, request=None):

    if request is None:
        request = TestBrowserRequest({})

    object = TestObject(id=5, title="Test", creator="strichter@yahoo.com",
                        data="Some data")
    return Edit(object, request)
