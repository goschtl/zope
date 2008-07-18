"""
Using the @grok.require decorator in a view class is not allowed.

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
  GrokError: The @grok.require decorator is used for method 'render' in view <class 'grokcore.view.tests.security.view_decorator.BogusView'>. It may only be used for XML-RPC methods.


"""
import zope.interface

from grokcore.view.tests import grok
import grokcore.view


class Bogus(grokcore.view.Permission):
    grok.name('bogus.perm')


class BogusView(grok.View):
    grok.context(zope.interface.Interface)

    @grokcore.view.require(Bogus)
    def render(self):
        pass
