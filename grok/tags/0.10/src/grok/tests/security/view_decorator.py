"""
Using the @grok.require decorator in a view class is not allowed.

  >>> grok.grok(__name__)
  Traceback (most recent call last):
  GrokError: The @grok.require decorator is used for method 'render' in view <class 'grok.tests.security.view_decorator.BogusView'>. It may only be used for XML-RPC methods.


"""

import grok
import zope.interface

grok.define_permission('bogus.perm')

class BogusView(grok.View):
    grok.context(zope.interface.Interface)

    @grok.require('bogus.perm')
    def render(self):
        pass
