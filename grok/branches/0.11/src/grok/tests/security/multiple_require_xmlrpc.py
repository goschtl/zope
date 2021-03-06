"""
Multiple calls of grok.require in one class are not allowed.

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
     ...
  GrokError: grok.require was called multiple times in <class 'grok.tests.security.multiple_require_xmlrpc.MultipleXMLRPC'>. It may only be set once for a class.
"""
import grok
import zope.interface

class One(grok.Permission):
    grok.name('permission.1')

class Two(grok.Permission):
    grok.name('permission.2')

class MultipleXMLRPC(grok.XMLRPC):
    grok.context(zope.interface.Interface)
    grok.require('permission.1')
    grok.require('permission.2')

    def render(self):
        pass
