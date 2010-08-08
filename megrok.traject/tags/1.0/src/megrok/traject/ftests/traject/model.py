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

  >>> getRootFolder()["app"] = app = App()

We set up a test browser:

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.handleErrors = False

We we traverse from the app URL, we expect things to happen::

  >>> browser.open("http://localhost/app/mammoths/Knuth")
  >>> print browser.contents
  The name of this mammoth is Knuth.

We can also go to another view::

  >>> browser.open("http://localhost/app/mammoths/Knuth/other")
  >>> print browser.contents
  This is indeed Knuth

We can also locate a mammoth::

  >>> mammoth = Mammoth('Dijkstra')
  >>> class Default(object):
  ...    def __init__(self, *args, **kw):
  ...        pass
  >>> traject.locate(app, mammoth, Default)
  >>> mammoth.__name__
  u'Dijkstra'
  >>> mammoth.__parent__
  <megrok.traject.ftests.traject.model.Default object at ...>

"""

import grok

from megrok import traject

class App(grok.Application, grok.Model):
    pass

class Mammoth(traject.Model):
    traject.context(App)
    traject.pattern('mammoths/:name')
    
    def __init__(self, name):
        self.name = name

    def factory(name):
        return Mammoth(name)

    def arguments(self):
        return dict(name=self.name)

class MammothIndex(grok.View):
    grok.context(Mammoth)
    grok.name('index')
    def render(self):
        return 'The name of this mammoth is %s.' % self.context.name

class MammothOther(grok.View):
    grok.context(Mammoth)
    grok.name('other')
    def render(self):
        return "This is indeed %s" % self.context.name
