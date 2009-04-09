##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.component import getMultiAdapter
  >>> context = Context()
  >>> request = TestRequest()

Let's test the viewlets support in Jinja2 templates.
Instead of <tal:block content="structure provider:manager" />
we use: {{ provider('manager')}} ::

  >>> view = getMultiAdapter((context, request), name='usingviewlets')
  >>> print view()
  Testing megrok.jinja with viewlets support
  From the view: A view variable
  From the viewlet: A viewlet variable
"""

from grokcore.component import Context, context, name
from grokcore.view import View
from grokcore.viewlet import Viewlet, ViewletManager, viewletmanager


class Context(Context):
    pass

class UsingViewlets(View):
    def update(self):
        self.something = 'A view variable'

class ViewletMgr(ViewletManager):
    context(Context)
    name('manager')

class Viewlet(Viewlet):
    context(Context)
    viewletmanager(ViewletMgr)

    def update(self):
        self.another = 'A viewlet variable'

