##############################################################################
#
# Copyright (c) 2006 by us.
#
##############################################################################
"""
$Id: views.py 72088 2007-01-18 01:09:33Z rogerineichen $
"""
__docformat__ = "reStructuredText"

from zope.viewlet import viewlet
from z3c.pagelet import browser


class IndexPagelet(browser.BrowserPagelet):
    """Default index view."""


Ready2GoCSS = viewlet.CSSViewlet('ready2go.css')


Ready2GoJavaScript = viewlet.JavaScriptViewlet('ready2go.js')
