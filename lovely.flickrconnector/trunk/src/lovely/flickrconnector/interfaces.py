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
"""Flickr Connector Interface

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
from lovely import flickr

class IFlickrConnector(flickr.interfaces.IFlickr):
    api_key = zope.schema.TextLine(
        title = u'FLickr API key'
    )
    shared_secret = zope.schema.TextLine(
        title = u'FLickr shared secret'
    )