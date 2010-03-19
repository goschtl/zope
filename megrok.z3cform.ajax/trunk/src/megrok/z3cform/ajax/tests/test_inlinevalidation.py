"""
Let's import and init the necessary work environment::

  >>> import grokcore.component as grok
  >>> from zope.testbrowser.testing import Browser

  >>> browser = Browser()
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/@@myform')
  >>> browser.headers['STATUS'].upper()
  '200 OK'

   
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.component import getMultiAdapter
  >>> from zope.traversing.interfaces import ITraversable

  >>> request = TestRequest() 
  >>> egon = Mammoth()
  >>> myform = getMultiAdapter((egon, request), name=u"myform")
  >>> myform
  <megrok.z3cform.ajax.tests.test_inlinevalidation.MyForm object at ...>

  >>> validator = getMultiAdapter((myform, request), ITraversable, name=u"validate")
  >>> validator
  <megrok.z3cform.ajax.validation.InlineValidation object at ...>

  >>> validator.update()
  >>> validator.validate(['name',])
  {'form-widgets-name': u'Required input is missing.'}


  >>> jsonvalidator = getMultiAdapter((validator, request), name=u"field")
  >>> jsonvalidator
  <grok.meta.Validators object at ...>

  >>> jsonvalidator.field('form.widgets.name')
  {'form-widgets-name': u'Required input is missing.'}
  
"""

import grokcore.view as grok

from grokcore.component import Context
from megrok.z3cform.ajax import InlineValidation 
from zope.interface import Interface
from zope.schema import TextLine
from megrok.z3cform.base import Form, Fields


class IMammoth(Interface):
    name = TextLine(title=u"Name")


class Mammoth(Context):
    pass


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
