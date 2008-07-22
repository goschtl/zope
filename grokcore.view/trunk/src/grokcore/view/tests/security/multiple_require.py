"""
Multiple calls of grok.require in one class are not allowed.

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
    ...
  GrokError: grok.require was called multiple times in <class 'grokcore.view.tests.security.multiple_require.MultipleView'>. It may only be set once for a class.

"""
import grokcore.view as grok
import zope.interface


class One(grok.Permission):
    grok.name('permission.1')


class Two(grok.Permission):
    grok.name('permission.2')


class MultipleView(grok.View):
    grok.context(zope.interface.Interface)
    grok.require(One)
    grok.require(Two)

    def render(self):
        pass
