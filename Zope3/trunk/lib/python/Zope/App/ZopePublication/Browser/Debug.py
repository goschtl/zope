##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""Zope 3 debugger

This is the first preliminary (add weasle words) cut at a zope debugger.

$Id: Debug.py,v 1.2 2002/06/10 23:29:20 jim Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from Zope.Publisher.Publish import publish as _publish
from Zope.App.ZopePublication.Browser.Publication import BrowserPublication
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.Configuration.xmlconfig import XMLConfig
from cStringIO import StringIO
import base64

XMLConfig('../../site.zcml')()
db= DB(FileStorage('../../Data.fs'))
pub = BrowserPublication(db)

def publish(path='/', stdin='', basic=None, **kw):
    out = StringIO()
    if type(stdin) is str:
        stdin = StringIO(stdin)
    env = {'PATH_INFO': path}
    env.update(kw)

    if basic:
        env['HTTP_AUTHORIZATION']="Basic %s" % base64.encodestring(basic)

    request = TestRequest(StringIO(''), StringIO(), env)
    request.setPublication(pub)

    _publish(request, 0)
