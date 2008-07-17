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

For each Trail you register, an IAbsoluteURL adapter is created so
that the objects you are wrapping can be assigned useful URLs.

  >>> getRootFolder()["app"] = app = App()
  >>> from zope.app.component.hooks import setSite
  >>> setSite(app)

The line that follows should not be necessary, but at the moment is,
possibly because the test suite groks things different than a production
instance:

  >>> Trail('/mammoth/:name', IMammoth) and None

Anyway:

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.handleErrors = False

When constructing the URL, any parameters are pulled off of the object
as attributes.  In the example below, the Mammoth URL is formed using
the parameter ":name", which will be filled in using the Mammoth's
attribute "mammoth.name".

  >>> browser.open("http://localhost/app")
  >>> print browser.contents
  The URL of the mammoth is http://localhost/app/mammoth/Knuth.

"""

import grok
from megrok.trails import TrailHead, Trail
from zope.interface import Interface

class IMammoth(Interface):
    """Interface of a Mammoth."""

class Mammoth(grok.Model):
    grok.implements(IMammoth)
    def __init__(self, name):
        self.name = name

class App(grok.Application, grok.Container):
    pass

class AppTrailHead(TrailHead):
    grok.context(App)
    trails = [
        Trail('/mammoth/:name', IMammoth),
        ]

class AppIndex(grok.View):
    grok.context(App)
    grok.name('index')
    def render(self):
        return 'The URL of the mammoth is %s.' % self.url(Mammoth('Knuth'))
