##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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

We create an app:

  >>> getRootFolder()["app"] = App()

We set up a test browser:

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

When we traverse to an object that doesn't exist, we expect an error::

  >>> browser.open("http://localhost/app/doesntexist")
  Traceback (most recent call last):
     ...
  httperror_seek_wrapper: HTTP Error 404: Not Found

"""

import grok

from megrok import traject

class Mammoth(grok.Model):
    def __init__(self, name):
        self.name = name

class MammothIndex(grok.View):
    grok.context(Mammoth)
    grok.name('index')
    def render(self):
        return 'The name of this mammoth is %s.' % self.context.name

class App(grok.Application, grok.Model):
    pass

class MammothTraject(traject.Traject):
    grok.context(App)

    pattern = 'mammoths/:name'
    model = Mammoth

    def factory(name):
        return Mammoth(name)

    def arguments(mammoth):
        return dict(name=mammoth.name)
