##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Smiley Configuration code

$Id: metaconfigure.py,v 1.1 2003/08/22 21:27:33 srichter Exp $
"""
import os

from zope.app import zapi
from zope.app.component.metaconfigure import utility
from zope.app.publisher.browser.resourcemeta import resource

from interfaces import ISmileyTheme
from globaltheme import GlobalSmileyTheme, declareDefaultSmileyTheme

__registered_resources = []

def registerSmiley(text, path, theme):
    theme = zapi.queryUtility(ISmileyTheme, theme)
    theme.provideSmiley(text, path)


class theme(object):

    def __init__(self, _context, name):
        self.name = name
        utility(_context, ISmileyTheme,
                factory=GlobalSmileyTheme, name=name)

    def smiley(self, _context, text, file):
        return smiley(_context, text, file, self.name)

    def __call__(self):
        return


def smiley(_context, text, file, theme):

    name = theme + '__' + os.path.split(file)[1]
    path = '/++resource++' + name

    if name not in __registered_resources:
        resource(_context, name, image=file)
        __registered_resources.append(name)

    _context.action(
        discriminator = ('smiley', theme, text),
        callable = registerSmiley,
        args = (text, path, theme),
        )


def defaultTheme(_context, name=None):
    _context.action(
        discriminator = ('smiley', 'defaultTheme',),
        callable = declareDefaultSmileyTheme,
        args = (name,),
        )

