##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
$Id$
"""
from paste.deploy import loadapp
from paste.fixture import TestApp
import sys
import os
import lovely.zetup.factory
from lovely.zetup.factory import reset
from zope.app.testing import setup
from zope.security.proxy import removeSecurityProxy
import wsgi_intercept.zope_testbrowser

_pasteApp = None

def getTestApp(**kwargs):
    return TestApp(getPasteApplication(), **kwargs)

def getPasteApplication():
    return _pasteApp

def getRootFolder(proxied=True):
    f = lovely.zetup.factory._app.requestFactory._publication._app
    if not proxied:
        return removeSecurityProxy(f)
    return f

def setUpInterceptServer(domain='nohost', port=80):
    wsgi_intercept.add_wsgi_intercept(domain, port, getPasteApplication)

class Browser(wsgi_intercept.zope_testbrowser.WSGI_Browser):

    def __init__(self, *args, **kwargs):
        super(Browser, self).__init__(*args, **kwargs)
        self.mech_browser.set_handle_robots(False)

class PasteAppLayer(object):

    """sets up a layer with an app"""

    __bases__ = ()
    __name__ = 'PasteAppLayer'

    def __init__(self, cfg):
        globs = sys._getframe(1).f_globals
        self.cfg = cfg
        self.there = os.path.dirname(globs['__file__'])

    def setUp(self):
        global _pasteApp
        _pasteApp = loadapp(self.cfg, relative_to=self.there)

    def tearDown(self):
        setup.placefulTearDown()
        reset()
        global _pasteApp
        _pasteApp = None
