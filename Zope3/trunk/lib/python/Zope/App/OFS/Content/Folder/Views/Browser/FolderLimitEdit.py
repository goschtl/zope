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
$Id: FolderLimitEdit.py,v 1.4 2002/09/04 13:44:27 faassen Exp $
"""
from Zope.App.Forms.Views.Browser.FormView import FormView 
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.App.OFS.Content.Folder.Folder import IFolder

class FolderLimitEdit(FormView):

    #__implements__ = (Form.__implements__,)

    name = 'limitForm'     
    schema = IFolder
    
    title = 'Folder Item Limit Form'
    description = ('This edit form allows you to ...')

    _fieldViewNames = ['LimitFieldView']

    template = ViewPageTemplateFile('limit.pt')  
