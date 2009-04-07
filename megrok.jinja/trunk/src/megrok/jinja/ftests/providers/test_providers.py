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

import grok

class Context(grok.Context):
    pass

class UsingViewlets(grok.View):
    def update(self):
        self.something = 'A view variable'

class ViewletMgr(grok.ViewletManager):
    grok.context(Context)
    grok.name('manager')

class Viewlet(grok.Viewlet):
    grok.context(Context)
    grok.viewletmanager(ViewletMgr)

    def update(self):
        self.another = 'A viewlet variable'

