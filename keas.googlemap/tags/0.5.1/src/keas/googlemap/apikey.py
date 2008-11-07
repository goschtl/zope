##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Google Map APIKey handling

$Id$
"""

import urlparse
import zope.component
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.viewlet.viewlet import ViewletBase

from keas.googlemap import interfaces

class APIKey(object):
    """See ``keas.googlemap.interfaces.IGoogleMapAPIKey``."""
    zope.interface.implements(interfaces.IGoogleMapAPIKey)

    key = FieldProperty(interfaces.IGoogleMapAPIKey['key'])

    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self.key)

LocalhostAPIKey = APIKey("ABQIAAAA8SpDMoY3XpgN5DzYnmNsmhTwM0brOpm-All5BF6PoaKBxRWWERT3cHSc49vCxDS6hLf1VMPD_e-ekg")

class APIKeyViewlet(ViewletBase):
    """A viewlet for inserting a script tag that loads the google maps API."""

    zope.component.adapts(
        zope.interface.Interface,
        IBrowserRequest,
        zope.interface.Interface,
        zope.interface.Interface)

    srcURLTemplate = "http://maps.google.com/maps?file=api&v=2&key=%s&async=2&callback=keas_googlemap_maploader"

    def render(self):
        domainName = urlparse.urlparse(self.request.getURL())[1].split(':')[0]
        apikey = zope.component.queryUtility(interfaces.IGoogleMapAPIKey, domainName)
        if apikey is None:
            return '<!-- Google Maps API Key not found for %s -->' % domainName
        srcURL = self.srcURLTemplate % apikey.key
        return '<script type="text/javascript"\nsrc="%s">\n</script>' % srcURL

class StaticAPIKeyViewlet(APIKeyViewlet):
    """A viewlet for static pages."""

    srcURLTemplate = "http://maps.google.com/maps?file=api&v=2&key=%s"
