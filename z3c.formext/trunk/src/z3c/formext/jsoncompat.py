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
"""ExtJS Component representation.

$Id$
"""
__docformat__ = "reStructuredText"

try:
    # the fast way
    import cjson
    encode = cjson.encode
    jsonDecode = cjson.decode
except ImportError:
    try:
        # the python 2.6 way
        import json
        encode = json.dumps
        jsonDecode = json.loads
    except ImportError:
        # the slow python < 2.6 way
        import simplejson
        encode = simplejson.dumps
        jsonDecode = simplejson.loads

from zope.i18n import translate

def translateObject(o):
    if isinstance(o, list):
        for index, value in enumerate(o):
            o[index] = translateObject(value)
    elif isinstance(o, tuple):
        o = [translateObject(value) for value in o]
    elif isinstance(o, dict):
        for key, value in o.items():
            o[key] = translateObject(value)
    elif isinstance(o, unicode):
        o = translate(o)
    return o

def jsonEncode(o):
    o = translateObject(o)
    return encode(o)
