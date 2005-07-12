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

configure_zcml = """
<configure 
    xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser"
    xmlns:i18n="http://namespaces.zope.org/i18n"
    >
  <configure package="Products.Five.tests">
    <i18n:registerTranslations directory="locales" />
  </configure>

  <configure package="Products.Five.browser.tests">
    <browser:page
        for="Products.Five.interfaces.IFolder"
        template="i18n.pt"
        name="i18n.html"
        permission="zope2.View"
        />
  </configure>
</configure>
"""

def setUp(test):
    from Products.Five.zcml import load_string
    load_string(configure_zcml)

def test_zpt_i18n():
    """
    In order to be able to traverse to the PageTemplate view, we need
    a traversable object:

      >>> from Products.Five.testing import manage_addFiveTraversableFolder
      >>> manage_addFiveTraversableFolder(self.folder, 'testoid', 'Testoid')

    We tell Zope to translate the messages by passing the
    ``Accept-Language`` header which is processed by the
    ``IUserPreferredLangauges`` adapter:

      >>> print http(r'''
      ... GET /test_folder_1_/testoid/@@i18n.html HTTP/1.1
      ... Accept-Language: de
      ... ''')
      HTTP/1.1 200 OK
      ...
      <html>
      <body>
      <p>Dies ist eine Nachricht</p>
      <p>Dies ist eine explizite Nachricht</p>
      <p>Dies sind 4 Nachrichten</p>
      <p>Dies sind 4 explizite Nachrichten</p>
      <table summary="Dies ist ein Attribut">
      </table>
      <table summary="Explizite Zusammenfassung"
             title="Expliziter Titel">
      </table>
      </body>
      </html>
      ...
    """

def test_suite():
    from Testing.ZopeTestCase import installProduct, FunctionalDocTestSuite
    installProduct('Five')
    from zope.testing.doctest import ELLIPSIS
    return FunctionalDocTestSuite(setUp=setUp, optionflags=ELLIPSIS)

if __name__ == '__main__':
    framework()
