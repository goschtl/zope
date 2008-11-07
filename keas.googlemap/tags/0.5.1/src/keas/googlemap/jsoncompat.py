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
"""Google Map JSON Support

$Id$
"""

try:
    import cjson
    encode = cjson.encode
    decode = cjson.decode
except ImportError:
    try:
        import json #python 2.6
        encode = json.dumps
        decode = json.loads
    except ImportError:
        import simplejson
        encode = simplejson.dumps
        decode = simplejson.loads
