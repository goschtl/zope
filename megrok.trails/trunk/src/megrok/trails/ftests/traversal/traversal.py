##############################################################################
#
# Copyright (c) 2007-2008 Zope Corporation and Contributors.
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
"""

A TrailHead is a special kind of grok.Traverser that attempts to match
URLs against a list of URL patterns, called Trails, that it contains.

  >>> getRootFolder()["app"] = App()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.handleErrors = False

When we traverse to a mammoth URL, the name is supplied as the
argument for its constructor.  In this example, having "Knuth" in
place of the ":name" in the URL pattern means that the Mammoth will be
instantiated as Mammoth(name="Knuth").

  >>> browser.open("http://localhost/app/mammoth/Knuth")
  >>> print browser.contents
  The name of this mammoth is Knuth.

"""

import grok
from megrok.trails import TrailHead, Trail
from zope.interface import Interface, implements

class IMammoth(Interface):
    """Interface for a Mammoth."""

class Mammoth(grok.Model):
    implements(IMammoth)
    def __init__(self, name):
        self.name = name

class MammothIndex(grok.View):
    grok.context(Mammoth)
    grok.name('index')
    def render(self):
        return 'The name of this mammoth is %s.' % self.context.name

class App(grok.Application, grok.Container):
    pass

class AppTrailHead(TrailHead):
    grok.context(App)
    trails = [
        Trail('/mammoth/:name', Mammoth),
        ]
