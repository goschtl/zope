##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Smiley Themes

Here is an example:

  First we need to prepare the system by creating and registering some themes.

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.app.tests import ztapi
  
  >>> import globaltheme
  
  >>> theme = globaltheme.GlobalSmileyTheme()
  >>> theme.provideSmiley(':-)', '++resource++plain__smile.png')
  >>> theme.provideSmiley(';-)', '++resource++plain__wink.png')
  >>> ztapi.provideUtility(ISmileyTheme, theme, 'plain')
  >>> globaltheme.declareDefaultSmileyTheme('plain')

  >>> theme = globaltheme.GlobalSmileyTheme()
  >>> theme.provideSmiley(':-]', '++resource++square__smile.png')
  >>> theme.provideSmiley(';-]', '++resource++square__wink.png')
  >>> ztapi.provideUtility(ISmileyTheme, theme, 'square')

  Now we can test the API calls.

  >>> getSmiley(':-)', TestRequest(), 'plain')
  '/++resource++plain__smile.png'
  >>> getSmiley(':-)', TestRequest())
  '/++resource++plain__smile.png'
  >>> getSmiley(':-)', TestRequest(), 'square')
  Traceback (most recent call last):
  ...
  ComponentLookupError: 'Smiley not found.'
  >>> getSmiley(':-]', TestRequest())
  Traceback (most recent call last):
  ...
  ComponentLookupError: 'Smiley not found.'

  >>> querySmiley(':-)', TestRequest(), 'plain')
  '/++resource++plain__smile.png'
  >>> querySmiley(':-)', TestRequest())
  '/++resource++plain__smile.png'
  >>> querySmiley(':-)', TestRequest(), 'square') is None
  True
  >>> querySmiley(':-]', TestRequest()) is None
  True

  >>> themes = getSmileyThemes()
  >>> themes.sort()
  >>> themes
  [u'plain', u'square']

  >>> map = getSmileysMapping(TestRequest(), 'plain')
  >>> map = map.items()
  >>> map.sort()
  >>> import pprint
  >>> pprint.pprint(map)
  [(':-)', '/++resource++plain__smile.png'),
   (';-)', '/++resource++plain__wink.png')]

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app import zapi

from interfaces import ISmileyTheme

def getSmiley(text, request, theme='default'):
    theme = zapi.getUtility(ISmileyTheme, theme)
    return theme.getSmiley(text, request)

def querySmiley(text, request, theme='default', default=None):
    theme = zapi.queryUtility(ISmileyTheme, theme)
    if theme is None:
        return default
    return theme.querySmiley(text, request, default)

def getSmileyThemes():
    return [name for name, util in zapi.getUtilitiesFor(ISmileyTheme)
            if name != 'default']

def getSmileysMapping(request, theme='default'):
    theme = zapi.getUtility(ISmileyTheme, theme)
    return theme.getSmileysMapping(request)
