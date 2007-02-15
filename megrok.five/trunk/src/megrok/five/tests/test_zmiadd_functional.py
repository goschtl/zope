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

  XXX The following test doesn't work due to a setup bug in the zope 2
  instance buildout recipe...

  #>>> 'megrok.five.tests.test_zmiadd_functional.TestApp' in add.displayOptions
  #True

"""
import grok
import megrok.five

class TestApp(megrok.five.Model, grok.Application):
    pass


def test_suite():
    import unittest
    from megrok.five.testing import FunctionalLayer
    from Testing.ZopeTestCase import FunctionalDocTestSuite

    suite = FunctionalDocTestSuite()
    suite.layer = FunctionalLayer
    return unittest.TestSuite([suite])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
