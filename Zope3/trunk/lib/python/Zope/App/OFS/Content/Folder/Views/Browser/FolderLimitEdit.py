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
$Id: FolderLimitEdit.py,v 1.3 2002/07/19 13:21:09 srichter Exp $
"""
from Zope.App.Forms.Views.Browser.FormView import FormView 
from Zope.App.PageTemplate import ViewPageTemplateFile


class FolderLimitEdit(FormView):

    #__implements__ = (Form.__implements__,)

    name = 'limitForm'     
    title = 'Folder Item Limit Form'
    description = ('This edit form allows you to ...')

    _fieldViewNames = ['LimitFieldView']

    template = ViewPageTemplateFile('limit.pt')  
