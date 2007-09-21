##############################################################################
#
# Copyright (c) 2006 by us.
#
##############################################################################
"""
$Id: views.py 72088 2007-01-18 01:09:33Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.app import zapi
from zope.viewlet import viewlet

from z3c.pagelet import browser
from z3c.skin.pagelet import interfaces


class IndexPagelet(browser.BrowserPagelet):
    """Default index view."""


PageletCSS = viewlet.CSSViewlet('pagelet.css')


PageletJavaScript = viewlet.JavaScriptViewlet('pagelet.js')
