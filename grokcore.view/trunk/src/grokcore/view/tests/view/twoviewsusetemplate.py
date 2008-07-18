"""
A template can be used by multiple views at the same time:

  >>> grok.testing.grok(__name__)

  >>> manfred = Mammoth()
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> from zope import component

  >>> view = component.getMultiAdapter((manfred, request), name='a')
  >>> print view()
  View A

  >>> view = component.getMultiAdapter((manfred, request), name='b')
  >>> print view()
  View A

It also works if templates are both associated explicitly:

  >>> view = component.getMultiAdapter((manfred, request), name='c')
  >>> print view()
  Template

  >>> view = component.getMultiAdapter((manfred, request), name='d')
  >>> print view()
  Template

Because the template is associated, we do not expect it to be
registered as its own view:

  >>> view = component.getMultiAdapter((manfred, request), name='templ')
  Traceback (most recent call last):
    ...
  ComponentLookupError:
  ((<grokcore.view.tests.view.twoviewsusetemplate.Mammoth object at 0x...>,
  <zope.publisher.browser.TestRequest instance URL=http://127.0.0.1>),
  <InterfaceClass zope.interface.Interface>, 'templ')


"""
from grokcore.view.tests import grok
import grokcore.view


class Mammoth(grok.Model):
    pass


class A(grok.View):
    pass


a = grokcore.view.PageTemplate("View A")


class B(grok.View):
    grokcore.view.template('a')


class C(grok.View):
    grokcore.view.template('templ')


class D(grok.View):
    grokcore.view.template('templ')


templ = grokcore.view.PageTemplate('Template')
