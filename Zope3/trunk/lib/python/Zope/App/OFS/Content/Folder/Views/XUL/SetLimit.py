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

$Id: SetLimit.py,v 1.2 2002/06/10 23:28:02 jim Exp $
"""

from Zope.App.Formulator.Form import Form
from Zope.App.PageTemplate import ViewPageTemplateFile


class SetLimit(Form):

    __implements__ = (Form.__implements__,)

    name = 'limitForm'     
    title = 'Folder Item Limit Form'
    description = ('This edit form allows you to ...')

    _fieldViewNames = ['XULLimitFieldView']

    template = ViewPageTemplateFile('limit.pt')
    action_js = ViewPageTemplateFile('action.pt')

    def action(self, limit):
        ''' '''
        self.context.setLimit(int(limit))
