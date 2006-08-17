##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Flickr Connector Implementation

$Id$
"""
__docformat__ = "reStructuredText"

import persistent
import zope.interface
from zope.app.container import contained
from zope.schema import fieldproperty
from lovely import flickr
from lovely.flickrconnector import interfaces

class FlickrConnector(persistent.Persistent, contained.Contained):
    zope.interface.implements(interfaces.IFlickrConnector)

    api_key = fieldproperty.FieldProperty(
        interfaces.IFlickrConnector['api_key'])
    shared_secret = fieldproperty.FieldProperty(
        interfaces.IFlickrConnector['shared_secret'])

    @property
    def auth(self):
        return flickr.auth.APIAuth(self.api_key, self.shared_secret)

    @property
    def photos(self):
        return flickr.test.APIPhoto(self.api_key, self.shared_secret)
    
    @property
    def test(self):
        return flickr.test.APITest(self.api_key, self.shared_secret)
    
    