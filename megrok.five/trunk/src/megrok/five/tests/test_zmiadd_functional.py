"""
  >>> import grok
  >>> grok.grok('megrok.five.tests.test_zmiadd_functional')

First, let's create a manager user with which we can access the ZMI:

  >>> uf = app.acl_users
  >>> uf._doAddUser('mgr', 'mgrpw', ['Manager'], [])

  >>> from Products.Five.testbrowser import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.open('http://localhost/manage_main')

  >>> add = browser.getControl(name=':action')
  >>> 'megrok.five.tests.test_zmiadd_functional.MammothManager' in add.displayOptions
  True

"""
import grok
import megrok.five

class MammothManager(megrok.five.Model, grok.Application):
    pass


def test_suite():
    import unittest
    from megrok.five.testing import FunctionalLayer
    from Testing.ZopeTestCase import FunctionalDocTestSuite

    suite = FunctionalDocTestSuite()
    suite.layer = FunctionalLayer
    return unittest.TestSuite([suite])
