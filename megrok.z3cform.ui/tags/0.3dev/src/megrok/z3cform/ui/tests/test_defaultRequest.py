"""
megrok.z3cform.ui
=================

We start with creating a TestReqeust:

   >>> from zope.publisher.browser import TestRequest
   >>> request = TestRequest()
   >>> request
   <zope.publisher.browser.TestRequest instance URL=http://127.0.0.1>

Let's check if the request provides the inteface IFormLayer

   >>> from z3c.form.interfaces import IFormLayer
   >>> IFormLayer.providedBy(request)
   True

and IDivFormLayer.

   >>> from z3c.formui.interfaces import IDivFormLayer
   >>> IDivFormLayer.providedBy(request)
   True

"""


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.ui.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

