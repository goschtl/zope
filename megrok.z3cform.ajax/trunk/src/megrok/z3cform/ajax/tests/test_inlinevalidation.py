"""
Let's import and init the necessary work environment::

  >>> import grokcore.component as grok
  >>> from zope.testbrowser.testing import Browser

  >>> browser = Browser()
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/@@myform')
  >>> browser.headers['STATUS'].upper()
  '200 OK'

  >>> browser.open('http://localhost/@@myform++validation++/field?fieldname=name')
  >>> browser.contents
"""

import grokcore.view as grok

from megrok.z3cform.ajax import InlineValidation 
from zope.interface import Interface
from zope.schema import TextLine
from megrok.z3cform.base import Form, Fields


class IMammoth(Interface):
    name = TextLine(title=u"Name")

class MyForm(Form):
    grok.context(Interface)
    fields = Fields(IMammoth)
    ignoreContext = True

    def update(self):
        InlineValidation.need()



def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.ajax.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite
