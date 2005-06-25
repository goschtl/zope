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

def test_browser_languages():
    """
    Let's setup the browser languages adapter.  The ``app`` object is
    kindly provided by ZopeTestCase

      >>> request = app.REQUEST
      >>> from zope.i18n.interfaces import IUserPreferredLanguages
      >>> languages = IUserPreferredLanguages(request)

    Without any ``Accept-Language`` HTTP header, the adapter will just
    return whatever has been specified in the localizer/PTS cookie
    variable:

      >>> request.cookies['LOCALIZER_LANGUAGE'] = 'de'
      >>> languages.getPreferredLanguages()
      ['de']
      >>> del request.cookies['LOCALIZER_LANGUAGE']

      >>> request.cookies['pts_language'] = 'de'
      >>> languages.getPreferredLanguages()
      ['de']
      >>> del request.cookies['pts_language']

    Without any cookie, the adapter will work like the original Zope 3
    one (extracting the ``Accept-Language`` header):

      >>> request['HTTP_ACCEPT_LANGUAGE'] = 'ro,en-us;q=0.8,es;q=0.5,fr;q=0.3'
      >>> languages.getPreferredLanguages()
      ['ro', 'en-us', 'es', 'fr']

    If any of the cookies are specified, it will be treated with
    priority.  A language specified in the cookie that is not in the
    HTTP headers will be prepended to the language list; if it already
    is in the language list, it will be moved up to the first position:

      >>> request.cookies['LOCALIZER_LANGUAGE'] = 'de'
      >>> languages.getPreferredLanguages()
      ['de', 'ro', 'en-us', 'es', 'fr']
      >>> request.cookies['LOCALIZER_LANGUAGE'] = 'es'
      >>> languages.getPreferredLanguages()
      ['es', 'ro', 'en-us', 'fr']
      >>> request.cookies['LOCALIZER_LANGUAGE'] = 'ro'
      >>> languages.getPreferredLanguages()
      ['ro', 'en-us', 'es', 'fr']

      >>> del request.cookies['LOCALIZER_LANGUAGE']

      >>> request.cookies['pts_language'] = 'de'
      >>> languages.getPreferredLanguages()
      ['de', 'ro', 'en-us', 'es', 'fr']
      >>> request.cookies['pts_language'] = 'es'
      >>> languages.getPreferredLanguages()
      ['es', 'ro', 'en-us', 'fr']
      >>> request.cookies['pts_language'] = 'ro'
      >>> languages.getPreferredLanguages()
      ['ro', 'en-us', 'es', 'fr']

    If both cookies are specified, localizer wins:

      >>> request.cookies['pts_language'] = 'es'
      >>> request.cookies['LOCALIZER_LANGUAGE'] = 'de'
      >>> languages.getPreferredLanguages()
      ['de', 'ro', 'en-us', 'es', 'fr']
    """

def test_suite():
    from Testing.ZopeTestCase import installProduct, ZopeDocTestSuite
    installProduct('Five')
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()
