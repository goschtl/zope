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
$Id: SchemaTestObject.py,v 1.1 2002/07/16 15:15:55 srichter Exp $
"""
import Schema
from Zope.App.Forms.Views.Browser import Widget

class Email(Schema.String):
    pass

class STestObject(Schema):

   id = Schema.String(
       id="id",
       title="Id",
       required=1)

   title = Schema.String(
       id="title",
       title="Title",
       required=0)

   data = Schema.String(
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
       

class TestObject:

    __schema__ = Schema

    id = None
    title = "Test Object"
    data = ''
    creator = ''


class Edit(FormView):

    schema = STestObject
    custom_widgets = {'creator': Widget.TextWidget(displaywidth=30),
                      'data': Widget.FileWidget()}
