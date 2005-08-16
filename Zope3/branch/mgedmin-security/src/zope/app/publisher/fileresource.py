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
"""

$Id: fileresource.py,v 1.4 2003/11/04 04:04:26 jeremy Exp $
"""
from zope.app.content_types import guess_content_type
from zope.app.datetimeutils import rfc1123_date
from time import time
import os

class File(object):
    
    def __init__(self, path):
        self.path = path

        f = open(path, 'rb')
        data = f.read()
        f.close()
        self.content_type, enc = guess_content_type(path, data)
        self.__name__ = path[path.rfind('/') + 1:]
        self.lmt = float(os.stat(path)[8]) or time()
        self.lmh = rfc1123_date(self.lmt)

class Image(File):
    """Image objects stored in external files."""

    def __init__(self, path):
        super(Image, self).__init__(path)
        if self.content_type in (None, 'application/octet-stream'):
            ext = os.path.splitext(self.path)[1]
            if ext:
                self.content_type = 'image/%s' % ext[1:]
