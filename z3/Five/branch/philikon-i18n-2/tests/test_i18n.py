##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests for the i18n framework

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.interface import implements
from zope.i18n.interfaces import IUserPreferredLanguages

def test_directive():
    """
    Let's register the gettext locales using the ZCML directive:

      >>> configure_zcml = '''
      ... <configure xmlns="http://namespaces.zope.org/zope"
      ...            xmlns:i18n="http://namespaces.zope.org/i18n"
      ...            package="Products.Five.tests">
      ...   <i18n:registerTranslations directory="locales" />
      ... </configure>'''

      >>> from Products.Five import zcml
      >>> zcml.load_string(configure_zcml)

    Now, take an arbitrary message id from that domain:

      >>> from zope.i18nmessageid import MessageIDFactory
      >>> from zope.i18n import translate
      >>> _ = MessageIDFactory('fivetest')
      >>> msg = _(u'explicit-msg', u'This is an explicit message')

    As you can see, both the default functionality and translation to
    German work:

      >>> translate(msg)
      u'This is an explicit message'
      >>> translate(msg, target_language='de')
      u'Dies ist eine explizite Nachricht'
    """

class DummyRequestLanguages(object):
    implements(IUserPreferredLanguages)

    def __init__(self, context):
        self.context = context

def test_request_adapter_dispatch():
    """By default, Five dispatches ``IUserPreferredLanguages`` adapter
    lookup to the request.  We shall test this here.

    First, we register our own languages adapter for the request (not
    for *):
 
      >>> configure_zcml = '''
      ... <configure xmlns="http://namespaces.zope.org/zope"
      ...            package="Products.Five.tests">
      ...   <adapter
      ...       for="zope.publisher.interfaces.http.IHTTPRequest"
      ...       provides="zope.i18n.interfaces.IUserPreferredLanguages"
      ...       factory="Products.Five.tests.test_i18n.DummyRequestLanguages"
      ...       />
      ... </configure>'''
      >>> from Products.Five import zcml
      >>> zcml.load_string(configure_zcml)

    Now we lookup the ``IUserPreferredLanguages`` adapter for an
    arbitrary object that can acquire the request, such as the test
    folder.  We expect to get the adapter we registered for
    ``IHTTPRequest``:

      >>> from Products.Five.tests.test_i18n import DummyRequestLanguages
      >>> from zope.i18n.interfaces import IUserPreferredLanguages
      >>> adapter = IUserPreferredLanguages(self.folder)
      >>> isinstance(adapter, DummyRequestLanguages)
      True
    """

def test_suite():
    from Testing.ZopeTestCase import installProduct, ZopeDocTestSuite
    installProduct('Five')
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()
