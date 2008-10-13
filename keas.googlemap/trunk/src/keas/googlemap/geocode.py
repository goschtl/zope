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
"""Keas Geocodes.

$Id$
"""

# Interesting Python library for geocoding here:
# http://code.google.com/p/geolocator/source/browse/trunk/geolocator/gislib.py

import urllib
from math import asin, sqrt, cos, sin, pi

from zope.component import adapts, adapter
from zope.interface import implements, implementer
from zope.schema.fieldproperty import FieldProperty
from zope.app.container.btree import BTreeContainer
import zope.annotation

from keas.googlemap import interfaces, apikey
from keas.googlemap import jsoncompat as json

GEOCODE_BASE = 'http://maps.google.com/maps/geo'

EARTH_RADIUS = 6372.795 #average
ONE_RADIAN = 180./pi


class Geocode(object):
    """See ``keas.googlemap.interfaces.IGeocode``."""

    implements(interfaces.IGeocode)
    adapts(interfaces.IHaveGeocode)

    latitude = FieldProperty(interfaces.IGeocode['latitude'])
    longitude = FieldProperty(interfaces.IGeocode['longitude'])

    def __init__(self, latitude=0.0, longitude=0.0):
        self.latitude = latitude
        self.longitude = longitude

    def update(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__,
                               self.latitude,
                               self.longitude)

class GeocodeQuery(object):
    """See ``keas.googlemap.interfaces.IGeocode``."""

    implements(interfaces.IGeocodeQuery)

    query = FieldProperty(interfaces.IGeocodeQuery['query'])

    def __init__(self, query):
        self.query = query

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__,
                           self.query)


@adapter(interfaces.IGeocodeQuery)
@implementer(interfaces.IGeocode)
def getGeocodeFromQuery(geoQuery):
    dict = { 'key'    : apikey.LocalhostAPIKey.key,
             'output' : 'json',
             'q'      : geoQuery.query }
    url = GEOCODE_BASE + '?' + urllib.urlencode(dict)
    info = json.decode(urllib.urlopen(url).read())
    if info['Status']['code'] == 200:
        coords = info['Placemark'][0]['Point']['coordinates']
        return Geocode(coords[1], coords[0])
    else:
        raise ValueError("Could not get geocode for %s" % dict['q'])

def getGeocodeFromAddr(street=u'', city=u'', state=u'', zipCode=u''):
    return getGeocodeFromQuery(GeocodeQuery(u','.join([street, city, state, zipCode])))


class CenteredGeocodes(list):
    """See ``keas.googlemap.interfaces.IGeocodes``."""

    implements(interfaces.ICenteredGeocodes)

    _center = FieldProperty(interfaces.ICenteredGeocodes['center'])
    def _getCenter(self):
        return self._center
    center = property(_getCenter)

    def __init__(self, center, *args):
        super(CenteredGeocodes, self).__init__()
        self._center = center
        self.add(args)

    def add(self, codes):
        for code in codes:
            distance = haversine(interfaces.IGeocode(self.center),
                                 interfaces.IGeocode(code)) * EARTH_RADIUS
            self.append((distance, code))
        self.sort()

    def sort(self):
        super(CenteredGeocodes, self).sort(key=lambda a: a[0])


def haversine(a, b):
    """calculate the haversine function on two geocodes."""
    rad = lambda a: a/ONE_RADIAN
    blat = rad(b.latitude)
    blon = rad(b.longitude)
    alat = rad(a.latitude)
    alon = rad(a.longitude)
    return 2*asin(sqrt(sin((blat-alat)/2)**2 + cos(alat)*cos(blat)*(sin((blon-alon)/2)**2)))



# adapter from IHaveGeocode to IGeocode
getGeocodeAnnotation = zope.annotation.factory(Geocode, 'keas.googlemap.geocode')
