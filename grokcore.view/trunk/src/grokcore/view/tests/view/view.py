"""

  >>> grok.testing.grok(__name__)

  >>> from zope.interface.verify import verifyObject
  >>> from grokcore.view.interfaces import IGrokView

We should find the ``cavepainting`` view for a mammoth:

  >>> manfred = Mammoth()
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> from zope import component
  >>> view = component.getMultiAdapter((manfred, request), name='cavepainting')
  >>> print view()
  A cave painting of a mammoth

  >>> view.context is manfred
  True
  >>> view.request is request
  True
  >>> verifyObject(IGrokView, view)
  True

Look up a view with a name explicitly set with ``grok.name``:

  >>> view = component.getMultiAdapter((manfred, request), name='meal')
  >>> print view()
  Mammoth burger
  >>> verifyObject(IGrokView, view)
  True

There's no view 'food':

  >>> view = component.getMultiAdapter((manfred, request), name='food')
  Traceback (most recent call last):
    ...
  ComponentLookupError: ((<grokcore.view.tests.view.view.Mammoth object at 0x...>, <zope.publisher.browser.TestRequest instance URL=http://127.0.0.1>), <InterfaceClass zope.interface.Interface>, 'food')

"""

import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class CavePainting(grok.View):
    pass

class Food(grok.View):
    """Grok says: ME NO SEE MAMMOTH, ME SEE MEAL!"""
    grok.name('meal')
    grok.template('meal')

