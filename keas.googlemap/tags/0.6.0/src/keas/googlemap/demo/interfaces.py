###############################################################################
#
# Copyright 2008 by Keas, Inc., San Francisco, CA
#
###############################################################################
"""Google Map Skin.

$Id$
"""
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app import rotterdam
from z3c.formui.interfaces import IDivFormLayer, ICSS as IFormUICSS
from z3c.form.interfaces import IFormLayer
from z3c.layer.pagelet import IPageletBrowserLayer
from zope.app.rotterdam import Rotterdam

from keas.googlemap.browser import IGoogleMapBrowserLayer


class IGoogleMapSkin(IDivFormLayer, IFormLayer, Rotterdam, IGoogleMapBrowserLayer):
    """Google Map Skin"""
