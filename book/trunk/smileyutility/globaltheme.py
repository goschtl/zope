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
"""Global Smiley Theme Implementation

$Id$
"""
__docformat__ = 'restructuredtext'
from zope.component.exceptions import ComponentLookupError
from zope.interface import implements

from zope.app import zapi
from zope.app.traversing.interfaces import IContainmentRoot

from interfaces import ISmileyTheme, IGlobalSmileyTheme

class Root(object):
    implements(IContainmentRoot)

def getRootURL(request):
    return str(zapi.getView(Root(), 'absolute_url', request))


class GlobalSmileyTheme(object):
    """A filesystem based smiley theme.

    Let's make sure that the global theme implementation actually fulfills the
    `ISmileyTheme` API.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IGlobalSmileyTheme, GlobalSmileyTheme)
    True

    Initialize the theme and add a couple of smileys.

    >>> theme = GlobalSmileyTheme()
    >>> theme.provideSmiley(':-)', '++resource++plain__smile.png')
    >>> theme.provideSmiley(';-)', '++resource++plain__wink.png')

    Let's try to get a smiley out of the registry.

    >>> from zope.publisher.browser import TestRequest

    >>> theme.getSmiley(':-)', TestRequest())
    '/++resource++plain__smile.png'
    >>> theme.getSmiley(':-(', TestRequest())
    Traceback (most recent call last):
    ...
    ComponentLookupError: 'Smiley not found.'
    >>> theme.querySmiley(';-)', TestRequest())
    '/++resource++plain__wink.png'
    >>> theme.querySmiley(';-(', TestRequest()) is None
    True

    And finally we's like to get a dictionary of all smileys. 
    
    >>> map = theme.getSmileysMapping(TestRequest())
    >>> len(map)
    2
    >>> map[':-)']
    '/++resource++plain__smile.png'
    >>> map[';-)']
    '/++resource++plain__wink.png'
    """
    implements(IGlobalSmileyTheme)

    def __init__(self):
        self.__smileys = {}

    def getSmiley(self, text, request):
        "See book.smileyutility.interfaces.ISmileyTheme"
        smiley = self.querySmiley(text, request)
        if smiley is None:
            raise ComponentLookupError, 'Smiley not found.'
        return smiley

    def querySmiley(self, text, request, default=None):
        "See book.smileyutility.interfaces.ISmileyTheme"
        if self.__smileys.get(text) is None:
            return default
        return getRootURL(request) + '/' + self.__smileys[text]

    def getSmileysMapping(self, request):
        "See book.smileyutility.interfaces.ISmileyTheme"
        smileys = self.__smileys.copy()
        root_url = getRootURL(request)
        for name, smiley in smileys.items():
            smileys[name] = root_url + '/' + smiley
        return smileys

    def provideSmiley(self, text, smiley_path):
        "See book.smileyutility.interfaces.IGlobalSmileyTheme"
        self.__smileys[text] = smiley_path


def declareDefaultSmileyTheme(name):
    """Declare the default smiley theme."""
    utilities = zapi.getService(zapi.servicenames.Utilities)
    theme = zapi.getUtility(ISmileyTheme, name)
    # register the utility simply without a name
    utilities.provideUtility(ISmileyTheme, theme, 'default')
