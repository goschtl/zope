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
"""Local Smiley Theme Implementation

$Id$
"""
__docformat__ = 'restructuredtext'
from zope.component.exceptions import ComponentLookupError
from zope.interface import implements

from zope.app import zapi
from zope.app.container.btree import BTreeContainer
from zope.app.component.localservice import getNextService
from zope.app.file.image import Image

from interfaces import ISmileyTheme, ISmiley, ILocalSmileyTheme

class Smiley(Image):
    implements(ISmiley)

class SmileyTheme(BTreeContainer):
    """A local smiley theme implementation.

    >>> import os
    >>> from zope.app.tests import setup
    >>> from zope.app.utility.utility import LocalUtilityService
    >>> import book.smileyutility
    >>> site = setup.placefulSetUp()
    >>> rootFolder = setup.buildSampleFolderTree()

    Setup a simple function to add local smileys to a theme.

    >>> def addSmiley(theme, text, filename):
    ...     base_dir = os.path.dirname(book.smileyutility.__file__)
    ...     filename = os.path.join(base_dir, filename)
    ...     theme[text] = Smiley(open(filename, 'r'))

    Create components in root folder

    >>> site = setup.createServiceManager(rootFolder)
    >>> utils = setup.addService(site, zapi.servicenames.Utilities,
    ...                         LocalUtilityService())
    >>> theme = SmileyTheme()
    >>> addSmiley(theme, ':)',  'smileys/plain/smile.png')
    >>> addSmiley(theme, ':(',  'smileys/plain/sad.png')
    >>> util = setup.addUtility(site, 'plain', ISmileyTheme, theme)

    Create components in `folder1`

    >>> site = setup.createServiceManager(rootFolder['folder1'])
    >>> utils = setup.addService(site, zapi.servicenames.Utilities,
    ...                          LocalUtilityService())
    >>> theme = SmileyTheme() 
    >>> addSmiley(theme, ':)',  'smileys/plain/biggrin.png')
    >>> addSmiley(theme, '8)',  'smileys/plain/cool.png')
    >>> util = setup.addUtility(site, 'plain', ISmileyTheme, theme)

    Now test the single smiley accessor methods

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.app.component.localservice import setSite
    >>> from book.smileyutility import getSmiley, querySmiley

    >>> setSite(rootFolder)
    >>> getSmiley(':)', TestRequest(), 'plain')
    'http://127.0.0.1/++etc++site/default/plain/%3A%29'
    >>> getSmiley(':(', TestRequest(), 'plain')
    'http://127.0.0.1/++etc++site/default/plain/%3A%28'
    >>> getSmiley('8)', TestRequest(), 'plain')
    Traceback (most recent call last):
    ...
    ComponentLookupError: '8)'
    >>> querySmiley('8)', TestRequest(), 'plain', 'nothing')
    'nothing'

    >>> setSite(rootFolder['folder1'])
    >>> getSmiley(':)', TestRequest(), 'plain')
    'http://127.0.0.1/folder1/++etc++site/default/plain/%3A%29'
    >>> getSmiley(':(', TestRequest(), 'plain')
    'http://127.0.0.1/++etc++site/default/plain/%3A%28'
    >>> getSmiley('8)', TestRequest(), 'plain')
    'http://127.0.0.1/folder1/++etc++site/default/plain/8%29'
    >>> getSmiley(':|', TestRequest(), 'plain')
    Traceback (most recent call last):
    ...
    ComponentLookupError: ':|'
    >>> querySmiley(':|', TestRequest(), 'plain', 'nothing')
    'nothing'
    
    Let's now test the `getSmileysMapping()` method. To do that we create a
    small helper method that helps us compare dictionaries.

    >>> from pprint import pprint
    >>> from book.smileyutility import getSmileysMapping
    >>> def output(dict):
    ...     items = dict.items()
    ...     items.sort()
    ...     pprint(items)

    >>> setSite(rootFolder)
    >>> output(getSmileysMapping(TestRequest(), 'plain'))
    [(u':(', 'http://127.0.0.1/++etc++site/default/plain/%3A%28'),
     (u':)', 'http://127.0.0.1/++etc++site/default/plain/%3A%29')]

    >>> setSite(rootFolder['folder1'])
    >>> output(getSmileysMapping(TestRequest(), 'plain'))
    [(u'8)', 'http://127.0.0.1/folder1/++etc++site/default/plain/8%29'),
     (u':(', 'http://127.0.0.1/++etc++site/default/plain/%3A%28'),
     (u':)', 'http://127.0.0.1/folder1/++etc++site/default/plain/%3A%29')]
    >>> getSmileysMapping(TestRequest(), 'foobar')
    Traceback (most recent call last):
    ...
    ComponentLookupError: \
(<InterfaceClass book.smileyutility.interfaces.ISmileyTheme>, 'foobar')

    >>> setup.placefulTearDown()
    """
    implements(ILocalSmileyTheme)

    def getSmiley(self, text, request):
        "See book.smileyutility.interfaces.ISmileyTheme"
        if text not in self:
            theme = queryNextTheme(self, zapi.name(self))
            if theme is None:
                raise ComponentLookupError(text)
            else:
                return theme.getSmiley(text, request)
        return getURL(self[text], request)
        
    def querySmiley(self, text, request, default=None):
        "See book.smileyutility.interfaces.ISmileyTheme"
        if text not in self:
            theme = queryNextTheme(self, zapi.name(self))
            if theme is None:
                return default
            else:
                return theme.querySmiley(text, request, default)
        return getURL(self[text], request)

    def getSmileysMapping(self, request):
        "See book.smileyutility.interfaces.ISmileyTheme"
        theme = queryNextTheme(self, zapi.name(self))
        if theme is None:
            smileys = {}
        else:
            smileys = theme.getSmileysMapping(request)

        for name, smiley in self.items():
            smileys[name] = getURL(smiley, request)

        return smileys


def queryNextTheme(context, name, default=None):
    """Get the next theme higher up."""
    utilities = getNextService(context, zapi.servicenames.Utilities)
    return utilities.queryUtility(ISmileyTheme, name, default)

def getURL(smiley, request):
    """Get the URL of the smiley."""
    url = zapi.getView(smiley, 'absolute_url', request=request)
    return url()
