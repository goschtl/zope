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

$Id: ZPTPageEdit.py,v 1.2 2002/06/10 23:28:06 jim Exp $
"""

from Zope.App.Formulator.Form import Form
from Zope.App.PageTemplate import ViewPageTemplateFile


class ZPTPageEdit(Form):

    __implements__ = Form.__implements__

    name = 'editForm'     
    title = 'Edit Form'
    description = ('This edit form allows you to make changes to the ' +
                   'source code of this ZPT Page.')

    _fieldViewNames = ['SourceFieldView']
    template = ViewPageTemplateFile('edit.pt')
